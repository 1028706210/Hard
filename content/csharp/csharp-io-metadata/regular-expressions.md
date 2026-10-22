---
id: csharp-io-metadata-regular-expressions
title: 正则表达式
concepts: [regular-expressions, strings]
objectives:
  - 使用 Regex 与捕获组从文本中按模式提取内容，并正确书写字符类与量词。
  - 区分正则的形状校验与语义校验边界，识别贪婪量词与重复匹配带来的常见陷阱。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/csharp/csharp-regular-expressions.html
source_snapshot_date: 2026-08-23
---

# 正则表达式

## 概念定义与适用场景

正则表达式用模式描述一类字符串，适合做格式校验、子串提取和批量替换。日志解析、模板占位符提取、输入格式粗检这类"形状匹配"问题是它的主场；一旦涉及嵌套结构或计数约束，就应该换用真正的解析代码。

```csharp
using System.Text.RegularExpressions;

var input = "订单 A-1024 已发货，订单 B-77 未发货";
foreach (Match match in Regex.Matches(input, @"[A-Z]-\d+"))
{
    Console.WriteLine(match.Value);
}
```

## 语法、API 与边界

`Regex.Matches` 返回输入中所有不重叠的匹配；用圆括号定义捕获组后，可以通过 `match.Groups[1].Value` 取出片段。字符类 `[a-z_]` 匹配集合中的单个字符，量词 `*`、`+`、`{m,n}` 控制重复次数。注意两个边界：`\d` 默认匹配所有 Unicode 十进制数字而不只是 ASCII 的 0-9；量词默认是贪婪的，`.*` 会尽可能多吃字符，需要时改用懒惰形式 `.*?`。正则只能验证形状，不能验证语义——`\d{4}-\d{2}-\d{2}` 会接受 `2026-13-40` 这种不存在的日期。

```csharp
using System.Text.RegularExpressions;

var template = "您好 {name}，积分 {points}";
Match match = Regex.Match(template, @"\{([a-z_]+)\}");
if (match.Success)
{
    Console.WriteLine(match.Groups[1].Value);
}
```

## 常见错误与实践建议

把用户输入直接拼进正则模式是高频事故：输入中的 `(`、`*` 等字符会改变模式含义甚至抛异常，应使用 `Regex.Escape` 转义。另一个常见误区是忘记 `Matches` 是"从左到右、不重叠"地扫描，指望一次匹配吃掉全文会漏掉后续片段。调试复杂模式时，先用最小的样例逐步加约束，再用需要拒绝的反例验证边界，比一次性写出长模式更可靠。
