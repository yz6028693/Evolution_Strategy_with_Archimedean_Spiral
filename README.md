Similar to Genetic Algorithm, the Evolution Strategy is a kind of Machine learning method without using derivative and backpropagation (used in common Neural Network) to find optimized solutions. Instead, it let the ‘environment’ to choose the best fit and learn from it to adapt to the environment (The idea of Evolution). 

The main goal of this demo is to apply Evolution Strategy algorithm to create points (red points) to find location of each random point (blue point) created from Archimedean Spiral curve.

The details of this demo can be accessed here: <a href = 'Evolution Strategy Algorithm and You.pdf'>Link</a>

Python package needed: 1. Numpy; 2. Matplotlib

<div style="overflow:hidden; width:98%;">
<div style="float: left; width: 48%;">

Old version without grouping (version 1):


<a><img src="Gif&Images/ES_OldVersion.gif" width = 50% position = 'ralative'></a>
</div>

<div style="float: left; width: 48%;">

Algorithm with separate group and parallel computing (version 2)：


<a><img src="Gif&Images/ES_WithGroup.gif" width = 50% position = 'ralative'></a>
</div>

<div style="float: left; width: 48%;">

New algorithm with multiprocessing and using Evolution Strategy to estimate gradient (version 3)：

The idea of this version is from a OpenAI's <a href = 'https://arxiv.org/pdf/1703.03864.pdf'>paper</a> and <a href = 'https://blog.openai.com/evolution-strategies/'>blog</a>. Their basic idea is to use Evolution Strategy to estimate gradient in the environment. I also applied multiprocessing in this version, as a rusult, different explorer is computed in different core. 

Note: 

1.You will mention in this version that even though I give different explorer different standard deviation (affect the max radius of its following points) and learning rate (affect their speed when move in this space) they will still easily get close to each other and do repeated work. This is because this 2-D space is relatively small and also different explorers can't communicate with each other to separte works. I will try to improve this in later versions. 

2. Adaptive standard deviation and learning rate will also add in following versions. (explorers with too small standard deviation and learning rate will move very slow while explorers with too big standard deviation and learning rate will shake among several blue planets)


<a><img src="Gif&Images/ESGradientExplorer.gif" width = 50% position = 'ralative'></a>
</div>


The Evolution Strategy is very flexible and can be used when we can translate our problem to a ‘environment’ where good or bad can be tell. In this demo, I consider each blue point as a planet, as a result, the environment of this demo looks like this (Rescaled gravitational field in this 2-D space):


<a><img src="Gif&Images/Environment.png" width = 50% position = 'ralative'></a>

</div>
