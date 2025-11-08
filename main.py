from fst_runtime.fst import Fst

def main():
    print("Hello from phonikud!")
    fst = Fst("phonikud.att")
    print(fst)
    #outputs = fst.down_generation('שָׁלוֹם עוֹלָם')
    text = "שלום"
    outputs = fst.down_generation(text)
    print(outputs)
    for out in outputs:
        print(out)


if __name__ == "__main__":
    main()
