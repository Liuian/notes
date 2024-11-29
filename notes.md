# Write Structured Code
- program flowchart
- dto
- dao
- Domain model

# Table of Contents
- [Stacking context; Z-index](#stacking-context-z-index)
- [Reading list](#reading-list)
- [`jq`檢查geojson檔案是否正確](#jq檢查geojson檔案是否正確)
  - [Installing jq on Windows](#installing-jq-on-windows)
  - [Use jq](#use-jq)

# Stacking context; Z-index
- 疊來疊去，堆疊順序(在上還是在下)
- [Stacking context](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_positioned_layout/Understanding_z-index/Stacking_context)

# reading list
- [編譯語言 VS 直譯語言](https://totoroliu.medium.com/%E7%B7%A8%E8%AD%AF%E8%AA%9E%E8%A8%80-vs-%E7%9B%B4%E8%AD%AF%E8%AA%9E%E8%A8%80-5f34e6bae051)
- 反組譯

# `jq`檢查geojson檔案是否正確
## Installing jq on Windows
- Download jq:https://jqlang.github.io/jq/download/

- Go to the jq releases page on GitHub.
- Download the jq-win64.exe (for 64-bit Windows) or jq-win32.exe (for 32-bit Windows).
- Rename the downloaded file to jq.exe.
- Add to System Path (optional but recommended):

- Move jq.exe to a folder like C:\Program Files\jq or another directory of your choice.
- Right-click on This PC or Computer on the desktop or in File Explorer, then select Properties.
- Click on Advanced system settings on the left, and then click the Environment Variables button.
- In the System variables section, find and select the Path variable, then click Edit.
- Click New and add the path to the folder where you placed jq.exe.
- Click OK to close all dialog boxes.

## Use jq:
- Open a new Command Prompt or PowerShell window.
- Run the command:`jq . C:\Users\ianliu\Downloads\ng_split_file_1.geojson`