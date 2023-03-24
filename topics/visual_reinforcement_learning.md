# Visual Reinforcement/Imitation/Robot Learning

- [Visual Reinforcement/Imitation/Robot Learning](#visual-reinforcementimitationrobot-learning)
  - [Demo Augmentation](#demo-augmentation)
  - [Data Augmentation](#data-augmentation)
  - [Learning by Watching](#learning-by-watching)
  - [Self-Supervised Learning](#self-supervised-learning)
  - [Pretraining](#pretraining)
  - [Multi-Task RL](#multi-task-rl)
  - [Model-Based RL](#model-based-rl)
  - [3D Vision](#3d-vision)
  - [Imitation Learning](#imitation-learning)
  - [Reward Learning](#reward-learning)
  - [Language Grounding](#language-grounding)
  - [Benchmark](#benchmark)

## Demo Augmentation
- NIPS 2022, [VRL3: A Data-Driven Framework for Visual Deep Reinforcement Learning](https://arxiv.org/abs/2202.10324)
- ICLR 2023, [MoDem: Accelerating Visual Model-Based Reinforcement Learning with Demonstrations](https://arxiv.org/abs/2212.05698)
- arXiv 2023, RLPD: [Efficient Online Reinforcement Learning with Offline Data](https://arxiv.org/abs/2302.02948)
- arXiv 2017, DDPGfD: [Leveraging Demonstrations for Deep Reinforcement Learning on Robotics Problems with Sparse Rewards](https://arxiv.org/abs/1707.08817)
- RSS 2018, DAPG: [Learning Complex Dexterous Manipulation with Deep Reinforcement Learning and Demonstrations](https://sites.google.com/view/deeprl-dexterous-manipulation)

## Data Augmentation
- ICLR 2023, [On the Data-Efficiency with Contrastive Image Transformation in Reinforcement Learning](https://openreview.net/forum?id=-nm-rHXi5ga)
- ICLR 2022, DrQ-v2: [Mastering Visual Continuous Control: Improved Data-Augmented Reinforcement Learning](https://arxiv.org/abs/2107.09645)
- NIPS 2020, RAD: [Reinforcement Learning with Augmented Data](https://mishalaskin.github.io/rad/)

## Learning by Watching
- arXiv 2023, [MimicPlay: Long-Horizon Imitation Learning by Watching Human Play](https://mimic-play.github.io/)
- CoRL 2022 oral, [Watch and Match: Supercharging Imitation with Regularized Optimal Transport](https://rot-robot.github.io/)

## Self-Supervised Learning
- CoRL 2022, MWM: [Masked World Models for Visual Control](https://sites.google.com/view/mwm-rl)
- NIPS 2022, [Does Self-supervised Learning Really Improve Reinforcement Learning from Pixels?](https://arxiv.org/abs/2206.05266)
- NIPS 2022, MLR: [Mask-based Latent Reconstruction for Reinforcement Learning](https://openreview.net/forum?id=-zlJOVc580)
- ICML 2022, [Phasic Self-Imitative Reduction for Sparse-Reward Goal-Conditioned Reinforcement Learning](https://proceedings.mlr.press/v162/li22g.html)
- ICLR 2021, [Learning Cross-Domain Correspondence for Control with Dynamics Cycle-Consistency](https://sjtuzq.github.io/cycle_dynamics.html)
- ICML 2021, ATC: [Decoupling Representation Learning from Reinforcement Learning](http://proceedings.mlr.press/v139/stooke21a.html)
- ICML 2021, [Reinforcement Learning with Prototypical Representations](https://arxiv.org/abs/2102.11271)
- ICML 2020, [CURL: Contrastive Unsupervised Representations for Reinforcement Learning](https://mishalaskin.github.io/curl/)
- NIPS 2019, [Unsupervised State Representation Learning in Atari](https://proceedings.neurips.cc/paper/2019/hash/6fb52e71b837628ac16539c1ff911667-Abstract.html)
- NIPS 2019, [Unsupervised Learning of Object Keypoints for Perception and Control](https://proceedings.neurips.cc/paper/2019/hash/dae3312c4c6c7000a37ecfb7b0aeb0e4-Abstract.html)
- RAL 2019, [Self-Supervised Correspondence in Visuomotor Policy Learning](https://arxiv.org/abs/1909.06933)

## Pretraining
- arXiv 2023, [What Makes Representation Learning from Videos Hard for Control?](https://tonyzhaozh.github.io/data/Video_Pretraining_Distribution_Shift.pdf)
  - a work from Finn's group
  - study visual representation from video for robotics
  - takeaway message: *while distribution shifts impact performance, we can often overcome these shortfalls through a combination of diversity coupled with test-time adaptation*
- ICLR 2023, [VIP: Towards Universal Visual Reward and Representation via Value-Implicit Pre-Training](https://sites.google.com/view/vip-rl)
- ICML 2022, PVR: [The (Un)Surprising Effectiveness of Pre-Trained Vision Models for Control](https://sites.google.com/view/pvr-control)
- NIPS 2022, [Pre-Trained Image Encoder for Generalizable Visual Reinforcement Learning](https://openreview.net/forum?id=E-0zNz5J5BM)
- CoRL 2022, [R3M: A Universal Visual Representation for Robot Manipulation](https://arxiv.org/abs/2203.12601)
- ICML 2021, [RRL: Resnet as representation for Reinforcement Learning](https://arxiv.org/abs/2107.03380)

## Multi-Task RL
- CoRL 2022, PerAct: [Perceiver-Actor: A Multi-Task Transformer for Robotic Manipulation](https://peract.github.io/)
- arXiv 2023, [Robust and Versatile Bipedal Jumping Control through Multi-Task Reinforcement Learning](https://arxiv.org/abs/2302.09450)
- arXiv 2022, GATO: [A Generalist Agent](https://www.deepmind.com/publications/a-generalist-agent)
- NIPS 2017, [Distral: Robust Multitask Reinforcement Learning](https://arxiv.org/abs/1707.04175)

## Model-Based RL
- arXiv 2023, DreamerV3: [Mastering Diverse Domains through World Models](https://arxiv.org/abs/2301.04104)
- ICLR 2023, [MoDem: Accelerating Visual Model-Based Reinforcement Learning with Demonstrations](https://arxiv.org/abs/2212.05698)
- ICLR 2023, [On the Feasibility of Cross-Task Transfer with Model-Based Reinforcement Learning ](https://openreview.net/forum?id=KB1sc5pNKFv)
- arXiv 2023, MV-MWM: [Multi-View Masked World Models for Visual Robotic Manipulation](https://sites.google.com/view/mv-mwm)
- ICML 2022, Diffuser: [Planning with Diffusion for Flexible Behavior Synthesis](https://diffusion-planning.github.io/)

## 3D Vision
- arXiv 2023, MV-MWM: [Multi-View Masked World Models for Visual Robotic Manipulation](https://sites.google.com/view/mv-mwm)
- ICRA 2023, [Feature-Realistic Neural Fusion for Real-Time, Open Set Scene Understanding](https://makezur.github.io/FeatureRealisticFusion/)
- CoRL 2022, [Semantic Abstraction: Open-World 3D Scene Understanding from 2D Vision-Language Models](https://semantic-abstraction.cs.columbia.edu/)
- arXiv 2020, [Keypoints into the future: Self-supervised correspondence in model-based reinforcement learning](https://arxiv.org/abs/2009.05085)
- ICML 2021. [Unsupervised Learning of Visual 3D Keypoints for Control](https://proceedings.mlr.press/v139/chen21b.html)
- CVPR 2022, [Coarse-to-Fine Q-attention: Efficient Learning for Visual Robotic Manipulation via Discretisation](https://arxiv.org/abs/2106.12534)

## Imitation Learning
- arXiv 2023, [Diffusion Policy: Visuomotor Policy Learning via Action Diffusion](https://diffusion-policy.cs.columbia.edu/)
- ICLR 2023, Diffusion-BC: [Imitating Human Behaviour with Diffusion Models](https://openreview.net/forum?id=Pv1GPQzRrC8)
- CoRL 2022, [VIOLA: Imitation Learning for Vision-Based Manipulation with Object Proposals Priors](https://ut-austin-rpl.github.io/VIOLA/)
- NIPS 2022, BeT: [Behavior Transformers: Cloning k modes with one stone](https://mahis.life/bet/)
- CoRL 2021, [BC-Z: Zero-Shot Task Generalization with Robotic Imitation Learning](https://sites.google.com/view/bc-z/home)
- NIPS 2017, [One-Shot Imitation Learning](https://sites.google.com/view/nips2017-one-shot-imitation/home)

## Reward Learning
- CoRL 2022, LIRF: [Training Robots to Evaluate Robots: Example-Based Interactive Reward Functions for Policy Learning](https://sites.google.com/view/lirf-corl-2022/)

## Language Grounding
- CoRL 2021, [CLIPort: What and Where Pathways for Robotic Manipulation](https://cliport.github.io/)

## Benchmark
- arXiv 2023, [ORBIT: A Unified Simulation Framework for Interactive Robot Learning Environments](https://isaac-orbit.github.io/)
- arXiv 2023, MJPC: [Predictive Sampling: Real-time Behaviour Synthesis with MuJoCo](https://arxiv.org/abs/2212.00541)
- CoRL 2022, [RoboTube: Learning Household Manipulation from Human Videos with Simulated Twin Environments](https://openreview.net/forum?id=VD0nXUG5Qk)
- CoRL 2020, [Meta-World: A Benchmark and Evaluation for Multi-Task and Meta Reinforcement Learning](https://meta-world.github.io/)
- RAL 2020, [RLBench: The Robot Learning Benchmark & Learning Environment](https://sites.google.com/view/rlbench)
