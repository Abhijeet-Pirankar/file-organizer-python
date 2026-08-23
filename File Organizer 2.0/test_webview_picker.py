import webview

def main():
    window = webview.create_window('', hidden=True)
    def open_dialog():
        result = window.create_file_dialog(webview.FOLDER_DIALOG)
        if result and len(result) > 0:
            print(result[0], end="")
        else:
            print("", end="")
        window.destroy()
        
    webview.start(open_dialog)

if __name__ == '__main__':
    main()
