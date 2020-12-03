from prompt_toolkit import prompt

if __name__ == "__main__":
    text = prompt('> ', vi_mode=True, multiline=True)
    print('You said: %s' % text)