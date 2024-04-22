<div align="center">

# [🤩AwesomePictureMusic](https://github.com/Yanyutin753/AwesomePictureMusic)
### 🎖️A python plugin for [Chatgpt On Wechat](https://github.com/zhayujie/chatgpt-on-wechat)，实现文本、图像、音乐和表情包之间相互转化，融合各种AI技术以构建丰富多变的工作流，为用户带来了充满惊喜的互动体验，同时也深度探索了AI的无限可能性！

<br>
</div>


## 支持列表

- [x] 支持📱表情包模型


- 通过爬虫和逆向工程，已经收集完完整的表情包数据集，一共22977条数据，且我们在[智谱清言](https://chatglm.cn)创建了一个智能体，欢迎体验：

- 🤩🤩🤩 →[点击查看智谱清言的回答](https://chatglm.cn/main/gdetail/66245f43ec988b0d3dd2904c)



## **项目指南**

### 本项目主要由以下几部分构成：

1. 💠 **文生图**： 我们将通过**sd**和**dall-e-3**两种方式，使用主机上的 stable diffusion 模型或调用 dall-e-3 API 模型，进行创新绘画，用文字带来新的视觉体验。

2. 🌓 **图生图**： 利用 stable diffusion，我们设置图像作为输入，并产生新的图像输出。详细的实现方式可参考 [pictureChange](https://github.com/Yanyutin753/pictureChange) 项目源码。

3. 💅 **图生文**： 通过调用我们的 API，使用特定视觉模型将图像转化为有意义的文本，尽可能完整、准确地描述图像内容。

4. 🪄 **图生音**：
   - 我们将通过 API 调用视觉模型来进行图片分析。
   - 之后，分析结果将作为 prompt 输入到 [suno](https://suno.ai/)，引导音乐创作。

5. 🧩 **文生音**： 我们会将获取到的文本作为 prompt 输入到 [suno](https://suno.ai/)，让这些文字在音乐中找到生命。

6. 📱 **文生表情包**： 
   - 我们计划使用开源的 [emo-visual-data](https://github.com/LLM-Red-Team/emo-visual-data) 数据集。同时，也会爬取一些新的表情包，并通过我的 API 进行表情包注解。
   - 不久的将来，我们将会通过[chatglm](https://chatglm.cn/)来创建一个属于我们自己的智能体。
   - 使用 [glm-free-api](https://github.com/LLM-Red-Team/glm-free-api) 允许我们调用智能体，执行文生表情包的操作。
   - 具体示例如下：
     <div align="center">
     <img src="https://github.com/Yanyutin753/clivia.github.io/assets/132346501/ab7d38a5-b286-4c30-a74d-1e03802e0f84" width="400" height="400">
     </div>

    - 具体操作如下：
     <div align="center">
     <img src="https://github.com/Yanyutin753/clivia.github.io/assets/132346501/470f99cf-d417-44cf-95a1-f3132a0e9e98" width="400" height="400">
     </div>

7. 📚 **整理代码**： 在所有开发工作完成后，我们将对代码进行仔细整理，以确保其整洁，并便于后续的维护和扩展。

8. 🛠️ **测试实践**： 确保代码和功能的正常运行非常关键。因此，我们会进行严格的测试实践，验证代码的功能并确认其能满足项目要求。


### ⚠️注意：
1. 请确认所有参与者都已在 Github 上创建账号。
2. 我们将在 Github 上进行所有代码的开发和维护，并在完成后提交最终的项目代码。


### 🧑‍🤝‍🧑贡献

<a href="https://github.com/Yanyutin753/AwesomePictureMusic/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=Yanyutin753/AwesomePictureMusic" />
</a>


### ❤️初心
- 我们的目标不仅是完成这个项目，也希望在此过程中提升我们的编码技巧和对 git 的熟练度，同时还可以把手试试一些有趣的新项目。我们会在 [pictureChange](https://github.com/Yanyutin753/pictureChange) 这个项目的基础上进行二次开发，以拓展其功能并实现我们的需求。
- 最后，我们将把代码合并到同一个分支，并推送到 Github。希望我们的项目可以获得更多的⭐️，让更多人看到我们的成果。
