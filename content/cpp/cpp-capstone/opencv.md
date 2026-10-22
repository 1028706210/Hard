---
id: cpp-capstone-opencv
title: C++ OpenCV
concepts: [arrays, data-structures]
objectives:
  - 会识别 cv::Mat 基础 API 与像素访问形态。
  - 会用纯数据 fixture 模拟图像阈值处理。
prerequisites: []
difficulty: advanced
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-opencv.html
source_snapshot_date: 2026-08-23
---

# C++ OpenCV

## 概念定义与适用场景

OpenCV 是计算机视觉库：cv::Mat 表示二维矩阵（图像），rows/cols 给尺寸，at<T>(y,x) 访问像素，threshold 做阈值化。本课程环境不安装 OpenCV，用 vector 嵌套模拟灰度矩阵即可复现同样的算法结构。

```cpp
// OpenCV 形态（本课不编译，仅 API 识别）：
// cv::Mat gray(rows, cols, CV_8UC1);
// int count = cv::countNonZero(gray >= threshold);
```

## 语法、API 与边界

灰度图每个像素是 0..255 的亮度值；阈值统计 = 遍历矩阵数出 >= 阈值的像素。行列索引先行后列（y 在前），与数学坐标相反。fixture 方案用 vector<vector<int>> 表达同一二维结构。

```cpp
#include <vector>

std::vector<std::vector<int>> gray{{10, 20}, {30, 40}};
int count = 0;
for (const auto& row : gray) {
    for (int pixel : row) {
        if (pixel >= 30) count++;
    }
}
```

## 常见错误与实践建议

常见错误：行列下标顺序颠倒、把 BGR 三通道图当灰度处理。不安装库也能先写纯算法再对接 cv::Mat。本课练习要求用纯数据 fixture 完成 3x3 灰度阈值统计。
