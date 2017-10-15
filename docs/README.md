# ChessBrain

Machine learning is one of the fastest-growing and most exciting fields out there, and deep learning represents its true bleeding edge. ChessBrain ​is a web application that leverages deep learning and
websockets to accomplish a complete solution for chess enthusiasts. What we are going to accomplish
in this project is to build a web platform which will be able to load a game of chess from any given
image that might contain a still frame of a chess board. This platform will enable players to set up a
chess board without the hassle of moving the pieces and setting it up yourself. Platform will feature a
chess engine for a solo play and will also support multiplayer.

## Work done so far

1. We have utilized the concepts of web scraping and used python (BeautifulSoup) to generate datasets by
scraping the chessboard images from chess.com, lichess.com and some other websites. To dissect a complete chessboard into individual chess pieces, we have used python imaging library PIL.

2. We made use of tensorflow and the concept of hough transform to identify chessboard in any
image. Since we are only considering digital images of chessboard from any particular website, we
operate on the base assumption that the chessboard will be aligned with the image. We used horizontal
and vertical gradient to identify all horizontal and vertical lines in the image and then isolated the lines associated with the chessboard. After identifying the chessboard we split the chessboard into 64
squares for further processing.

3. We have created a image classifier with 12 different classifications for chess pieces of both colors. It is created by training a Convolutional Neural Network with around 50 images of each possible
classification. Right now, the accuracy of classification is around 93%. The implementation of
CNN is done in Python and we are using Tensorflow for doing fast computations. The model
is being trained on cloud instead of local machines as our local machines don’t have enough processing
power and training a ConvNet requires quite good processing power.