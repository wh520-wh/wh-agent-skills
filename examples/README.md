# Examples

此目录用于存放真实运行产物样例。

## 如何生成

```powershell
# 使用准备好的测试视频
python "../scripts/prepare_video_understanding.py" `
  "path/to/test-video.mp4" `
  --work-dir "." `
  --interval 10
```

生成后将 `manifest.json`、联系表、关键帧截图复制到此目录。

## 预期产物

- `manifest.json` — 帧清单
- `contact_sheets/` — 联系表
- `manual.docx` — 示例手册（可选）
- `manual.pdf` — 示例手册（可选）
