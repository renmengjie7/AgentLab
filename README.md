<div align="center">
    <img src="./images/logo_stable-diffusion-xl.jpg" height=400 alt="logo"/>
</div>

# 🥳 AISimuToolKit: Use language models to simulate experiments

<p align="center">
    <a href="https://pypi.org/project/AISimuToolKit/">
        <img alt="PyPI" src="https://img.shields.io/pypi/v/AISimuToolKit?color=gree">
    </a>
</p>

## 🥷🏼 Quick Install

``` shell
conda create -n AISimu python==3.10
pip install AISimuToolKit
python demo_leaderless_discuss.py
python demo_detective.py
```

## 🥸 Functions
1. Use LLM to simulate agents with different profiles
2. Serial and parallel experiment
3. Memory compression => summary, reflection and finetune
4. A kit for simulation experiments


## 👀 Demo
1. **Serial example**    [demo_leaderless_discuss.py](demo_leaderless_discuss.py)  
**<u>Background</u>** Four people, Alice, Sophia, Jerre and Benjamin with different profiles are interviewing to be volunteers for the Olympics. This is a leaderless panel. The topic of discussion was "Minority language volunteers take half an hour to get to the site. As the only volunteer on site, now how will you inform foreigners of minority language that they must wear masks before entering the site"  
**<u>Result</u>**
<div align="center">
    <img src="./images/demo_leaderless_discussion_1.jpg" height=400 alt="demo_leaderless_discussion_1"/>
</div>
<div align="center">
    <img src="./images/demo_leaderless_discussion_2.jpg" height=300 alt="demo_leaderless_discussion_2"/>
</div>


2. **Parallel example** [demo_detective.py](demo_detective.py)
**<u>Background</u>**  
**<u>Result</u>**



## 👋 Contributing 

## 🙇 References & Thanks
1. LOGO from https://clipdrop.co/stable-diffusion
2. Reflect from https://arxiv.org/abs/2304.03442
