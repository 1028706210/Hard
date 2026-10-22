"""Apply reviewed concept slots without reformatting unrelated YAML."""
from pathlib import Path
import json
import re
import yaml

ROOT = Path(__file__).resolve().parents[3]
AUDIT = Path(__file__).parent
target = ROOT/'content/concepts.yaml'
original = target.read_bytes()
(AUDIT/'concepts-before.yaml').write_bytes(original)
text = original.decode('utf-8-sig').replace('\r\n', '\n')
changes = []

def replace_slot(concept_id, language, slot):
    global text
    pattern = re.compile(r'(?ms)^  - id: '+re.escape(concept_id)+r'\n.*?(?=^  - id: |\Z)')
    match = pattern.search(text)
    assert match, concept_id
    concept = match.group()
    language_pattern = re.compile(r'(?ms)^      '+language+r':\n.*?(?=^      [a-z]+:|\Z)')
    previous = language_pattern.search(concept)
    assert previous, (concept_id, language)
    lines = [f'      {language}:']
    for key, value in slot.items():
        if key == 'code' and value is not None:
            lines += ['        code: |', *['          '+line for line in value.rstrip().splitlines()]]
        else:
            lines.append(f'        {key}: '+json.dumps(value, ensure_ascii=False))
    replacement = '\n'.join(lines)+'\n'
    concept = concept[:previous.start()]+replacement+concept[previous.end():]
    text = text[:match.start()]+concept+text[match.end():]
    changes.append({'concept_id':concept_id,'language':language,'lesson_id':slot['lesson_id']})

python = json.loads((AUDIT/'python/mapping-suggestions.json').read_text(encoding='utf-8'))
for item in python['suggestions']:
    replace_slot(item['concept_id'], 'python', item['suggested_compare'])

java = json.loads((AUDIT/'java/mapping-suggestions.json').read_text(encoding='utf-8'))
for item in java['suggestions']:
    replace_slot(item['concept_id'], 'java', item['java'])

data = yaml.safe_load(text)
by_id = {item['id']:item for item in data['concepts']}
csharp = json.loads((AUDIT/'csharp/mapping-suggestions.json').read_text(encoding='utf-8'))
for item in csharp['suggestions']:
    if item['concept_id'] == 'references':
        continue  # object references are not the existing C++ alias concept
    slot = dict(by_id[item['concept_id']]['compare']['csharp'])
    slot['summary'] = item['suggested_summary']
    slot['lesson_id'] = item['lesson_id']
    replace_slot(item['concept_id'], 'csharp', slot)

# Correct overstatements in existing shared explanations as well.
text = text.replace('绑定既有对象的别名，必须初始化且不可改绑。', '以 C++ 左值引用为例，初始化时绑定既有对象的别名，之后赋值不会改绑。')
text = text.replace('与指针分离：引用不能为空、无需解引用语法，生命周期语义更安全。', '引用不提供空值状态且不能改绑，但仍可能悬垂；生命周期必须由调用方与被调用方约定。')
text = text.replace('无 switch 原生结构（以 if 链或字典分发替代），for 是对可迭代对象的遍历。', 'for 遍历可迭代对象；Python 3.10 起提供 match/case 结构模式匹配，与传统 switch 语义不同。')
text = text.replace('switch 表达式可以把分支作为值返回，模式匹配能力最强。', 'switch 表达式可返回值，并能结合类型、属性和关系模式描述分支。')
text = text.replace('函数重载在编译期决议，内联与模板实例化让抽象几乎零运行开销。', '函数重载在编译期决议；内联与模板可帮助优化，但实际开销仍取决于实现、使用方式与编译结果。')
text = text.replace('类型系统统一为值类型与引用类型，全部隐式继承 object。', '普通值类型与引用类型可通过 object 统一处理，值类型通常涉及装箱；指针、ref struct 等有额外限制。')
text = text.replace('与 Java 同为静态类型，但提供 var 推断与可空引用标注，空值检查更严格。', '与 Java 同为静态类型，var 进行编译期推断；可空引用标注提供编译器分析，并非运行时禁止 null。')
yaml.safe_load(text)
target.write_bytes(text.replace('\n','\r\n').encode('utf-8') if b'\r\n' in original else text.encode('utf-8'))

# Add only tags required by reviewed slots. Stable IDs and exercise data stay intact.
tag_changes = []
lessons = {}
for path in (ROOT/'content').glob('*/*/*.md'):
    content = path.read_text(encoding='utf-8-sig')
    match = re.search(r'^id: ([^\n]+)', content, re.M)
    if match: lessons[match.group(1).strip()] = path
for item in changes:
    path = lessons[item['lesson_id']]
    raw = path.read_bytes()
    content = raw.decode('utf-8-sig')
    match = re.search(r'^concepts: \[([^\]]*)\]', content, re.M)
    assert match
    tags = [value.strip() for value in match.group(1).split(',') if value.strip()]
    if item['concept_id'] not in tags:
        tags.append(item['concept_id'])
        changed = content[:match.start()]+'concepts: ['+', '.join(tags)+']'+content[match.end():]
        path.write_bytes(changed.encode('utf-8'))
        tag_changes.append({'lesson_id':item['lesson_id'],'added':item['concept_id']})
(AUDIT/'mapping-integration.json').write_text(json.dumps({'slots_updated':changes,'tag_changes':tag_changes,'csharp_references':'Not applied: class object-reference semantics do not by themselves teach C++ alias references.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'Updated {len(changes)} reviewed slots; added {len(tag_changes)} required tags.')
