# short key
- 從某一位置一次選取多行: `Alt + Shift`

# VS Code Python Tool Does Multiple Interactive Windows
- [VS Code Python Tool Does Multiple Interactive Windows](https://visualstudiomagazine.com/articles/2020/08/13/vs-code-python.aspx)
- Just open the settings page (File > Preferences > Settings), search for `interactive window mode` and change the setting value to `perFile`. Now when you run cells from different files, they will each run on their own separate window."

# remote ssh
1. install extension in vscode
    - install remote ssh, it will also install other two extension
    - ![alt text](./image/vscode-1.png)

2. Set Up SSH Configuration
    - Open the Command Palette by pressing `Ctrl + Shift + P` and type `Remote-SSH: Open Configuration File`.
    - Select the SSH configuration file to edit (usually ~/.ssh/config).
    - ![alt text](./image/vscode-3.png)
3. Connect to the Remote Server
    - Open the Command Palette again (`Ctrl + Shift + P`) and type `Remote-SSH: Connect to Host`.
    - Select the my_remote_server entry (or whatever name you used).
    - VS Code will connect to the remote server and open a new window.
    - ![alt text](./image/vscode-2.png)
4. Select Miniconda Python Environment
    - After connecting to the remote server, press `Ctrl + Shift + P` again and search for `Python: Select Interpreter`.

- TODO: 查這個jupyter是怎麼連上server的，port是多少，config是哪個檔案

# vscode-pandoc
- https://marketplace.visualstudio.com/items?itemName=DougFinke.vscode-pandoc
- https://github.com/jgm/pandoc/releases/tag/3.5
1. download `pandoc-3.5-windows-x86_64.msi`
2. install
3. press `F1` search `pandoc rendor`, and press document type wanted
- note that there should not have word file opened in the computer, or will show error