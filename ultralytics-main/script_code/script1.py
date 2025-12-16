import matplotlib.pyplot as plt
import pandas
import seaborn as sns
from numpy.ma.extras import average

# txt path
path = "C:/Users/baowu/Desktop/tmp.txt"

# open and reading the file
def output1():
    preprocess = []
    inference = []
    postprocess = []

    with open(path) as f:
        content = f.readlines()
        for i in range(len(content)):
            if i % 2 != 0:
                preprocess.append(eval(((content[i].strip()).split(' '))[1].strip('ms')))
                inference.append(eval(((content[i].strip()).split(' '))[3].strip('ms')))
                postprocess.append(eval(((content[i].strip()).split(' '))[5].strip('ms')))

    sns.set_theme(style="whitegrid")
    df = pandas.DataFrame({
        "preprocess speed": preprocess,
        "inference speed": inference,
        "postprocess speed": postprocess,
    })
    plt.title("Batch processing efficiency")
    plt.xlabel('Number of images')
    plt.ylabel('Speed (milliseconds)')
    sns.lineplot(data=df[["preprocess speed","inference speed","postprocess speed"]], linewidth=2)
    plt.show()

def output2():
    preprocess = []
    inference = []
    postprocess = []

    with open(path) as f:
        content = f.readlines()
        for i in range(len(content)):
            if i % 2 != 0:
                preprocess.append(eval(((content[i].strip()).split(' '))[1].strip('ms')))
                inference.append(eval(((content[i].strip()).split(' '))[3].strip('ms')))
                postprocess.append(eval(((content[i].strip()).split(' '))[5].strip('ms')))

    average_preprocess = average(preprocess)
    average_inference = average(inference)
    average_postprocess = average(postprocess)
    data = [average_preprocess, average_inference, average_postprocess]
    sns.set_theme(style="whitegrid")
    df = pandas.DataFrame({
        "data": data,
        "labels": ["preprocess average", "inference average", "postprocess average"]
    })
    plt.title("Average batch processing result")
    plt.ylabel('Average speed (milliseconds)')
    sns.barplot(data=df,y='data',x='labels')
    plt.show()


def main():
    output2()

if __name__ == '__main__':
    main()