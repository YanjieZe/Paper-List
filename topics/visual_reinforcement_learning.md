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
  - [Added from README inbox](#added-from-readme-inbox)

## Added from README inbox
- [arXiv 2026.09](https://arxiv.org/abs/2609.28660), Morphometric Imitation
- arXiv 2025.03, Scalable Real2Sim: Physics-Aware Asset Generation Via Robotic Pick-and-Place Setups, [website](https://scalable-real2sim.github.io/)
- arXiv 2025.02, DemoGen: Synthetic Demonstration Generation for Data-Efficient Visuomotor Policy Learning, [website](https://demo-generation.github.io/)
- arXiv 2024.12, **Genesis**: A Generative and Universal Physics Engine for Robotics and Beyond, [website](https://genesis-embodied-ai.github.io/)
- arXiv 2024.11, Inference-Time Policy Steering through Human Interactions, [arXiv](https://arxiv.org/abs/2411.16627)
- SIGGRAPH ASIA 2024, **CBIL**: Collective Behavior Imitation Learning for Fish from Real Videos, [website](https://frank-zy-dou.github.io/projects/CBIL/index.html)
- arXiv 2024.09 / CoRL 2024 Oral, **Robot See Robot Do**: Imitating Articulated Object Manipulation with Monocular 4D Reconstruction, [Website](https://robot-see-robot-do.github.io/)
- arXiv 2024.08, **Body Transformer**: Leveraging Robot Embodiment for Policy Learning, [arXiv](https://arxiv.org/abs/2408.06316)
- arXiv 2024.07, A Simulation Benchmark for **Autonomous Racing** with Large-Scale Human Data, [Website](https://assetto-corsa-gym.github.io/)
- arXiv 2024.07, **EquiBot**: SIM(3)-Equivariant Diffusion Policy for Generalizable and Data Efficient Learning, [Website](https://equi-bot.github.io/)
- arXiv 2024.07, **Sparse Diffusion Policy**: A Sparse, Reusable, and Flexible Policy for Robot Learning, [arXiv](https://arxiv.org/abs/2407.01531) / [Website](https://forrest-110.github.io/sparse_diffusion_policy/)
- arXiv 2024.07, **Open-TeleVision**: Teleoperation with Immersive Active Visual Feedback, [Website](https://robot-tv.github.io/)
- arXiv 2024.05, **Model-based Diffusion** for Trajectory Optimization, [Website](https://lecar-lab.github.io/mbd/)
- arXiv 2024.05, **TRANSIC**: Sim-to-Real Policy Transfer by Learning from Online Correction, [Website](https://transic-robot.github.io/)
- RSS 2024, **Natural Language** Can Help Bridge the Sim2Real Gap, [arXiv](https://arxiv.org/abs/2405.10020)
- RSS 2024, **Consistency Policy**: Accelerated Visuomotor Policies via Consistency Distillation, [Website](https://consistency-policy.github.io/)
- arXiv 2024.05, Evaluating Real-World Robot Manipulation Policies in Simulation, [Website](https://simpler-env.github.io/)
- arXiv 2024.05, **IntervenGen**: Interventional Data Generation for Robust and Data-Efficient Robot Imitation Learning, [arXiv](https://arxiv.org/abs/2405.01472)
- arXiv 2015.09, **MPPI**: Model Predictive Path Integral Control using Covariance Variable Importance Sampling, [arXiv](https://arxiv.org/abs/1509.01149)
- arXiv 2023.07, Sampling-based Model Predictive Control Leveraging Parallelizable Physics Simulations, [arXiv](https://arxiv.org/abs/2307.09105) / [Github](https://github.com/tud-airlab/mppi-isaac)
- arXiv 2024.04, **Policy-Guided Diffusion**, [arXiv](https://arxiv.org/abs/2404.06356) / [Github](https://github.com/EmptyJackson/policy-guided-diffusion)
- arXiv 2024.03, **Keypoint Action Tokens** Enable In-Context Imitation Learning in Robotics, [Website](https://www.robot-learning.uk/keypoint-action-tokens)
- arXiv 2024.03, **OPEN TEACH**: A Versatile Teleoperation System for Robotic Manipulation, [arXiv](https://arxiv.org/abs/2403.07870)
- CVPR 2024, **Hierarchical Diffusion Policy** for Kinematics-Aware Multi-Task Robotic Manipulation, [arXiv](https://arxiv.org/abs/2403.03890) / [Website](https://yusufma03.github.io/projects/hdp/)
- arXiv 2024.03, Reconciling Reality through Simulation: A **Real-to-Sim-to-Real** Approach for Robust Manipulation, [Website](https://real-to-sim-to-real.github.io/RialTo/)
- arXiv 2024.02, **Diffusion Meets DAgger**: Supercharging Eye-in-hand Imitation Learning, [Website](https://sites.google.com/view/diffusion-meets-dagger)
- arXiv 2024.02, Dynamics-Guided Diffusion Model for **Robot Manipulator Design**, [Website](https://dgdm-robot.github.io/)
- arXiv 2024.01, Generative Expressive Robot Behaviors using Large Language Models, [arXiv](https://arxiv.org/abs/2401.14673)
- ICLR 2024 oral, **ASID**: Active Exploration for System Identification and Reconstruction in Robotic Manipulation, [OpenReview](https://openreview.net/forum?id=jNR6s6OSBT)
- NIPS 2023, **Provable Guarantees for Generative Behavior Cloning**: Bridging Low-Level Stability and High-Level Behavior, [OpenReview](https://openreview.net/forum?id=PhFVF0gwid)
- 2023.10, Non-parametric regression for robot learning on manifolds, [arXiv](https://arxiv.org/abs/2310.19561)
- arXiv 2023.10, **EquivAct**: SIM(3)-Equivariant Visuomotor Policies beyond Rigid Object Manipulation, [Website](https://equivact.github.io/)
- arXiv 2023.10, Mastering Robot Manipulation with Multimodal Prompts through Pretraining and Multi-task fine-tuning, [arXiv](https://arxiv.org/abs/2310.09676)
- arXiv 2023.09, **GELLO**: A General, Low-Cost, and Intuitive Teleoperation Framework for Robot Manipulators, [Website](https://wuphilipp.github.io/gello_site/) / [arXiv](https://arxiv.org/abs/2309.13037)
- arXiv 2023.07, Waypoint-Based Imitation Learning for Robotic Manipulation, [Website](https://lucys0.github.io/awe/)
- arXiv 2023.07, **SpawnNet**: Learning Generalizable Visuomotor Skills from Pre-trained Networks, [Website](https://xingyu-lin.github.io/spawnnet/) / [Github](https://github.com/johnrso/spawnnet)
- AAAI 2023, Improving Long-Horizon Imitation Through Instruction Prediction, [arXiv](https://arxiv.org/abs/2306.12554) / [Github](https://github.com/jhejna/instruction-prediction)
- arXiv 2023.06, Robot Learning with Sensorimotor Pre-training, [arXiv](https://arxiv.org/abs/2306.10007) / [Website](https://robotic-pretrained-transformer.github.io/)
- arXiv 2023.05, **Optimus**: Imitating Task and Motion Planning with Visuomotor Transformers, [Website](https://mihdalal.github.io/optimus/)
- ICML 2023, **VIMA**: General Robot Manipulation with Multimodal Prompts, [Website](https://vimalabs.github.io/) / [Github](https://github.com/vimalabs/VIMA)
- arXiv 2023.04, **CoTPC**: Chain-of-Thought Predictive Control, [Website](https://zjia.eng.ucsd.edu/cotpc)
- arXiv 2023, For Pre-Trained Vision Models in Motor Control, Not All Policy Learning Methods are Created Equal, [arXiv](https://arxiv.org/abs/2304.04591)
- arXiv 2023, Learning Fine-Grained Bimanual Manipulation with Low-Cost Hardware, [Website](https://tonyzhaozh.github.io/aloha/)

## Demo Augmentation
- NIPS 2022, VRL3: A Data-Driven Framework for Visual Deep Reinforcement Learning, [arXiv](https://arxiv.org/abs/2202.10324)
- ICLR 2023, MoDem: Accelerating Visual Model-Based Reinforcement Learning with Demonstrations, [arXiv](https://arxiv.org/abs/2212.05698)
- arXiv 2023, RLPD: Efficient Online Reinforcement Learning with Offline Data, [arXiv](https://arxiv.org/abs/2302.02948)
- arXiv 2017, DDPGfD: Leveraging Demonstrations for Deep Reinforcement Learning on Robotics Problems with Sparse Rewards, [arXiv](https://arxiv.org/abs/1707.08817)
- RSS 2018, DAPG: Learning Complex Dexterous Manipulation with Deep Reinforcement Learning and Demonstrations, [Website](https://sites.google.com/view/deeprl-dexterous-manipulation)


## Data Augmentation
- ICLR 2023, On the Data-Efficiency with Contrastive Image Transformation in Reinforcement Learning, [OpenReview](https://openreview.net/forum?id=-nm-rHXi5ga)
- ICLR 2022, DrQ-v2: Mastering Visual Continuous Control: Improved Data-Augmented Reinforcement Learning, [arXiv](https://arxiv.org/abs/2107.09645)
- NIPS 2020, RAD: Reinforcement Learning with Augmented Data, [Website](https://mishalaskin.github.io/rad/)



## Learning by Watching
- arXiv 2023, MimicPlay: Long-Horizon Imitation Learning by Watching Human Play, [Website](https://mimic-play.github.io/)
- CoRL 2022 oral, Watch and Match: Supercharging Imitation with Regularized Optimal Transport, [Website](https://rot-robot.github.io/)




## Self-Supervised Learning
- CoRL 2022, MWM: Masked World Models for Visual Control, [Website](https://sites.google.com/view/mwm-rl)
- NIPS 2022, Does Self-supervised Learning Really Improve Reinforcement Learning from Pixels?, [arXiv](https://arxiv.org/abs/2206.05266)
- NIPS 2022, MLR: Mask-based Latent Reconstruction for Reinforcement Learning, [OpenReview](https://openreview.net/forum?id=-zlJOVc580)
- ICML 2022, Phasic Self-Imitative Reduction for Sparse-Reward Goal-Conditioned Reinforcement Learning, [Proceedings](https://proceedings.mlr.press/v162/li22g.html)
- ICLR 2021, Learning Cross-Domain Correspondence for Control with Dynamics Cycle-Consistency, [Website](https://sjtuzq.github.io/cycle_dynamics.html)
- ICML 2021, ATC: Decoupling Representation Learning from Reinforcement Learning, [Proceedings](http://proceedings.mlr.press/v139/stooke21a.html)
- ICML 2021, Reinforcement Learning with Prototypical Representations, [arXiv](https://arxiv.org/abs/2102.11271)
- ICML 2020, CURL: Contrastive Unsupervised Representations for Reinforcement Learning, [Website](https://mishalaskin.github.io/curl/)
- NIPS 2019, Unsupervised State Representation Learning in Atari, [Proceedings](https://proceedings.neurips.cc/paper/2019/hash/6fb52e71b837628ac16539c1ff911667-Abstract.html)
- NIPS 2019, Unsupervised Learning of Object Keypoints for Perception and Control, [Proceedings](https://proceedings.neurips.cc/paper/2019/hash/dae3312c4c6c7000a37ecfb7b0aeb0e4-Abstract.html)
- RAL 2019, Self-Supervised Correspondence in Visuomotor Policy Learning, [arXiv](https://arxiv.org/abs/1909.06933)


## Pretraining
- arXiv 2023, What Makes Representation Learning from Videos Hard for Control?, [PDF](https://tonyzhaozh.github.io/data/Video_Pretraining_Distribution_Shift.pdf)
- ICLR 2023, VIP: Towards Universal Visual Reward and Representation via Value-Implicit Pre-Training, [Website](https://sites.google.com/view/vip-rl)
- ICML 2022, PVR: The (Un)Surprising Effectiveness of Pre-Trained Vision Models for Control, [Website](https://sites.google.com/view/pvr-control)
- NIPS 2022, Pre-Trained Image Encoder for Generalizable Visual Reinforcement Learning, [OpenReview](https://openreview.net/forum?id=E-0zNz5J5BM)
- CoRL 2022, R3M: A Universal Visual Representation for Robot Manipulation, [arXiv](https://arxiv.org/abs/2203.12601)
- ICML 2021, RRL: Resnet as representation for Reinforcement Learning, [arXiv](https://arxiv.org/abs/2107.03380)

## Multi-Task RL
- CoRL 2022, PerAct: Perceiver-Actor: A Multi-Task Transformer for Robotic Manipulation, [Website](https://peract.github.io/)
- arXiv 2023, Robust and Versatile Bipedal Jumping Control through Multi-Task Reinforcement Learning, [arXiv](https://arxiv.org/abs/2302.09450)
- arXiv 2022, GATO: A Generalist Agent, [DeepMind](https://www.deepmind.com/publications/a-generalist-agent)
- NIPS 2017, Distral: Robust Multitask Reinforcement Learning, [arXiv](https://arxiv.org/abs/1707.04175)


## Model-Based RL
- arXiv 2023, DreamerV3: Mastering Diverse Domains through World Models, [arXiv](https://arxiv.org/abs/2301.04104)
- ICLR 2023, On the Feasibility of Cross-Task Transfer with Model-Based Reinforcement Learning, [OpenReview](https://openreview.net/forum?id=KB1sc5pNKFv)
- arXiv 2023, MV-MWM: Multi-View Masked World Models for Visual Robotic Manipulation, [Website](https://sites.google.com/view/mv-mwm)
- ICML 2022, Diffuser: Planning with Diffusion for Flexible Behavior Synthesis, [Website](https://diffusion-planning.github.io/)

## 3D Vision
- ICRA 2023, Feature-Realistic Neural Fusion for Real-Time, Open Set Scene Understanding, [Website](https://makezur.github.io/FeatureRealisticFusion/)
- CoRL 2022, Semantic Abstraction: Open-World 3D Scene Understanding from 2D Vision-Language Models, [Website](https://semantic-abstraction.cs.columbia.edu/)
- CVPR 2022, Coarse-to-Fine Q-attention: Efficient Learning for Visual Robotic Manipulation via Discretisation, [arXiv](https://arxiv.org/abs/2106.12534)
- ICML 2021, Unsupervised Learning of Visual 3D Keypoints for Control, [Website](https://proceedings.mlr.press/v139/chen21b.html)
- arXiv 2020.09, Keypoints into the future: Self-supervised correspondence in model-based reinforcement learning, [arXiv](https://arxiv.org/abs/2009.05085)


## Imitation Learning
- arXiv 2023, Diffusion Policy: Visuomotor Policy Learning via Action Diffusion, [Website](https://diffusion-policy.cs.columbia.edu/)
- ICLR 2023, Diffusion-BC: Imitating Human Behaviour with Diffusion Models, [OpenReview](https://openreview.net/forum?id=Pv1GPQzRrC8)
- CoRL 2022, VIOLA: Imitation Learning for Vision-Based Manipulation with Object Proposals Priors, [Website](https://ut-austin-rpl.github.io/VIOLA/)
- NIPS 2022, BeT: Behavior Transformers: Cloning k modes with one stone, [Website](https://mahis.life/bet/)
- CoRL 2021, BC-Z: Zero-Shot Task Generalization with Robotic Imitation Learning, [Website](https://sites.google.com/view/bc-z/home)
- NIPS 2017, One-Shot Imitation Learning, [Website](https://sites.google.com/view/nips2017-one-shot-imitation/home)


## Reward Learning
- CoRL 2022, LIRF: Training Robots to Evaluate Robots: Example-Based Interactive Reward Functions for Policy Learning, [Website](https://sites.google.com/view/lirf-corl-2022/)


## Language Grounding
- CoRL 2021, **CLIPort**: What and Where Pathways for Robotic Manipulation, [Website](https://cliport.github.io/) / [Github](https://github.com/cliport/cliport)

## Benchmark
- arXiv 2023, ORBIT: A Unified Simulation Framework for Interactive Robot Learning Environments, [Website](https://isaac-orbit.github.io/)
- arXiv 2023, MJPC: Predictive Sampling: Real-time Behaviour Synthesis with MuJoCo, [arXiv](https://arxiv.org/abs/2212.00541)
- CoRL 2022, RoboTube: Learning Household Manipulation from Human Videos with Simulated Twin Environments, [OpenReview](https://openreview.net/forum?id=VD0nXUG5Qk)
- CoRL 2020, Meta-World: A Benchmark and Evaluation for Multi-Task and Meta Reinforcement Learning, [Website](https://meta-world.github.io/)
- RAL 2020, RLBench: The Robot Learning Benchmark & Learning Environment, [Website](https://sites.google.com/view/rlbench)
