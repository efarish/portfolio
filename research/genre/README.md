# Project: Music Genre Classification Using FMA Dataset

Using  a dataset released with this [paper](https://arxiv.org/abs/1612.01840), MLP and CNN models are trained for music genre classification. The dataset consists of 917 GiB of 106,574 MP3 audio files. The models were used to classify the MP3 data into one of 16 genres. Example genres are Electronic, Experimental, Folk, Hip-Hop, Instrumental, International, Pop, and Rock.  

![tracks](https://github.com/efarish/portfolio/assets/165571745/8b869a12-49bf-4ebf-998c-b970cfe4f8e6)

## MLP Performance

Keras and scikit-learn where used to train MLP models and used a randomized grid search of 5-fold cross-validation to find an optimized set of hyper-parameters. Among the hyper-parameters optimized were the number of layers, layer nodes, dropout, epochs, batch size, and batch normalization. The datasets examined contained 8k, 25k, and 45k MP3 files. 

The dataset used for training were pre-extracted features released with paper mentioned above. The features consist of a number of audio spectra including Fourier transforms, Mel-frequence cepstral coefficients (MFCC) and Chroma CQT. These spectra were summarized into 7 summary statistics: Kurtosis, max value, min value, mean, median, skew, and standard deviation. These are the features used to train the models.

Below is a summary of the MLP performances by dataset. Auto-encoders were used in an attempt to reduce the number of features used during training and are labeled as "AE" below. 

![mlp](https://github.com/efarish/portfolio/assets/165571745/e945ed1b-ef03-4229-adf6-e08de36c58bb)

While a best test accuracy of 64% doesn't seem impressive, this must be contextualized with the fact that there were 16 possible classification for each MP3 file. 

## CNN Performance

Keras was used to train a convolutional neural network (CNN). Due to the amount of time required to create image files and do training, only 3 types of genres will included: Pop, Rock, and Electronic. Furthermore, only the small dataset consisting of 8k MP3 files will be used. Two types of datasets were used:

1.  30 second MP3 file clips
2.  3 second MP3 clips

Using those files, Mel-Spectrogram image files were created and these were the images used for training. An example is below.

![mel](https://github.com/efarish/portfolio/assets/165571745/078dacc1-ae45-4990-9dc8-bb9b6ca8d110)

5-fold CV was done by dividing training images into 5 folders, using 4 for training and 1 for validation. To avoid data bledding issues, clips taken from the same song were either placed in the training or validation datasets. Below is a summary of the performances.

![cnn](https://github.com/efarish/portfolio/assets/165571745/1b0cb36f-a70b-4be4-ad50-b25b29a3752d)

## Performance Summary

Per the data collected above:

1. Per the MLP summary, using more data improves performance.
2. There is a benefit to breaking the MP3 files into smaller clips.
3. The CNN has better performance for comparable amounts of data.  













