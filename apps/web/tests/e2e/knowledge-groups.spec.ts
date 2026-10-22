import { expect, test } from '@playwright/test';
import type { ChainConcept, ChainCourse } from '../../src/features/map/constellation';

test('every authored concept remains reachable with catalog-valid language bridges', async ({ page, request }) => {
  await page.setExtraHTTPHeaders({ 'X-Hard-E2E-Client': 'desktop' });
  const { concepts }: { concepts: ChainConcept[] } = await (await request.get('/api/compare/concepts')).json();
  const { courses }: { courses: ChainCourse[] } = await (await request.get('/api/content/catalog')).json();
  await page.goto('/');
  await expect(page.getByLabel('切换共同概念')).toBeVisible();
  expect(concepts).toHaveLength(45);
  for (const concept of concepts) {
    await page.getByLabel('切换共同概念').selectOption(concept.id);
    const valid = courses.filter(course => {
      const slot = concept.slots[course.language];
      return slot?.status === 'available' && course.modules.some(module => module.lessons.some(lesson => lesson.id === slot.lesson_id));
    });
    await expect(page.locator('[data-connection]')).toHaveCount(valid.length);
    await expect(page.locator('.concept-star.selected:not(:disabled)')).toHaveCount(valid.length);
    await expect(page.locator('.shared-star')).toContainText(concept.name);
    for (const course of valid) {
      await expect(page.locator(`[data-connection-detail="${course.language}"] a`)).toHaveAttribute('href', `/lesson/${concept.slots[course.language].lesson_id}`);
    }
  }
});
