# Project: Music Genre Classification Using FMA Dataset

Using  a dataset released with this [paper](https://arxiv.org/abs/1612.01840), MLP and CNN models. The dataset consists of 917 GiB of 106,574 MP3 audio files. MLP and CNN models will attempt to classify the MP3 data into one of 16 genres. Example genres are Electronic, Experimental, Folk, Hip-Hop, Instrumental, International, Pop, and Rock.  

![tracks](https://github.com/efarish/portfolio/assets/165571745/8b869a12-49bf-4ebf-998c-b970cfe4f8e6)

## MLP Performance

Keras and scikit-learn where used to train MLP models and used a randomized grid search of 5-fold cross-validation to find an optimized set of hyper-parameters. Among the hyper-parameters optimized were the number of layers, layer nodes, dropout, epochs, batch size, and batch normalization. The datasets examined contained 8k, 25k, and 45k MP3 files. 

The dataset used for training used pre-extracted features released with paper mentioned above. The feature consisted of a number of audio spectra including Fourier transforms, Mel-frequence cepstral coefficients (MFCC) and Chroma CQT. These spectra were summarized into 7 summary statistics: Kurtosis, max value, min value, mean, median, skew, and standard deviation.

Below is a summary of the MLP performances by dataset. Auto-encoders were used in an attempt to reduce the number of features used during training and are labeled as "AE" below. 

![mlp](https://github.com/efarish/portfolio/assets/165571745/e945ed1b-ef03-4229-adf6-e08de36c58bb)

While a best test accuracy of 64% doesn't seem impressive, this must be contextualized with the fact that there were 16 possible classification for each MP3 file. 







