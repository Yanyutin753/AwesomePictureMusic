import plugins
from bridge.context import ContextType
from bridge.reply import ReplyType
from plugins import *
from plugins.pictureChange.message import message_reply as MessageReply, message_type
from plugins.pictureChange.message.message_limit import MessageLimit
from plugins.pictureChange.work.common import Common
from .adminService.adminService import adminService

@plugins.register(name="pictureChange", desc="利用百度云AI和stable-diffusion webui来画图,图生图", version="1.8.5",
                  author="yang yang")
class pictureChange(Plugin):
    # 定义了模型枚举类型
    class Model(Enum):
        MODEL_1 = "anything-v5-PrtRE.safetensors [7f96a1a9ca]"
        MODEL_2 = "absolutereality_v181.safetensors [463d6a9fe8]"
        MODEL_3 = "QteaMix-fp16.safetensors [0c1efcbbd6]"

    def __init__(self):
        super().__init__()
        cursor = os.path.dirname(__file__)
        config_path = os.path.join(cursor, "config.json")
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)

                # 用于stable_diffusion参数
                self.rules = config["rules"]
                self.defaults = config["defaults"]
                self.default_params = self.defaults["params"]
                self.default_options = self.defaults["options"]
                self.role_options = config["roles"]
                self.start_args = config["start"]
                self.host = config["start"]["host"]
                self.port = config["start"]["port"]
                self.use_https = config["start"]["use_https"]

                #  用于变换和放大图片操作
                self.file_url = config["file_url"]

                # 用于聊天操作
                self.is_group_bot_name = conf().get("group_chat_prefix", [""])[0]
                self.single_bot_name = conf().get("single_chat_reply_prefix", [""])[0]
                self.other_user_id = config["use_group"]

                # 用于翻译prompt
                self.is_use_fanyi = config["is_use_fanyi"]
                self.baidu_api_key = config["baidu_api_key"]
                self.baidu_secret_key = config["baidu_secret_key"]

                # 用于音乐分析
                self.music_model = config["music_model"]

                # 用于图片和文件分析
                self.openai_api_key = config["openai_api_key"]
                self.openai_api_base = config["openai_api_base"]
                self.image_recognize_model = config["image_recognize_model"]
                self.file_recognize_model = config["file_recognize_model"]
                self.image_recognize_prompt = config["image_recognize_prompt"]
                self.file_recognize_prompt = config["file_recognize_prompt"]

                self.negative_prompt = ("(((nsfw))),EasyNegative,badhandv4,ng_deepnegative_v1_75t,(worst quality:2), "
                                        "(low quality:2), (normal quality:2), lowres, ((monochrome)), ((grayscale)), "
                                        "bad anatomy,DeepNegative, skin spots, acnes, skin blemishes,(fat:1.2),"
                                        "facing away, looking away,tilted head, lowres,bad anatomy,bad hands, "
                                        "missing fingers,extra digit, fewer digits,bad feet,poorly drawn hands,"
                                        "poorly drawn face,mutation,deformed,extra fingers,extra limbs,extra arms,"
                                        "extra legs,malformed limbs,fused fingers,too many fingers,long neck,"
                                        "cross-eyed,mutated hands,polar lowres,bad body,bad proportions,"
                                        "gross proportions,missing arms,missing legs,extra digit, extra arms, "
                                        "extra leg, extra foot,teethcroppe,signature, watermark, username,blurry,"
                                        "cropped,jpeg artifacts,text,error,Lower body exposure")

                self.bot_prompt = '''作为 Stable Diffusion Prompt 提示词专家，您将从关键词中创建提示，通常来自 Danbooru 
                等数据库。提示通常描述图像，使用常见词汇，按重要性排列，并用逗号分隔。避免使用"-"或"."，但可以接受空格和自然语言。避免词汇重复。为了强调关键词，请将其放在括号中以增加其权重。例如，"( 
                flowers)"将'flowers'的权重增加1.1倍，而"(((flowers)))"将其增加1.331倍。使用"( 
                flowers:1.5)"将'flowers'的权重增加1.5倍。只为重要的标签增加权重。提示包括三个部分：前缀（质量标签+风格词+效果器）+ 主题（图像的主要焦点）+ 
                场景（背景、环境）。前缀影响图像质量。像"masterpiece"、"best 
                quality"、"4k"这样的标签可以提高图像的细节。像"illustration"、"lensflare"这样的风格词定义图像的风格。像"bestlighting"、"lensflare 
                "、"depthoffield"这样的效果器会影响光照和深度。主题是图像的主要焦点，如角色或场景。对主题进行详细描述可以确保图像丰富而详细。增加主题的权重以增强
                其清晰度。对于角色，描述面部、头发、身体、服装、姿势等特征。场景描述环境。没有场景，图像的背景是平淡的，主题显得过大。某些主题本身包含场景（例如建筑物
                、风景）。像"花草草地"、"阳光"、"河流"这样的环境词可以丰富场景。你的任务是设计图像生成的提示。请按照以下步骤进行操作：我会发送给您一个图像场景。生成
                详细的图像描述，输出 Positive Prompt ,并确保用英文回复我。示例：我发送：二战时期的护士。您回复：A WWII-era nurse in a German uniform, 
                holding a wine bottle and stethoscope, sitting at a table in white attire,with a table in the background, masterpiece, 
                best quality, 4k, illustration style, best lighting, depth of field, detailed character,detailed environment.'''

                self.max_number = int(config["max_number"])
                self.max_size = int(config["max_size"])
                self.use_pictureChange = config["use_pictureChange"]
                # 管理员操作
                self.admin = adminService()
            self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
            logger.info("[pictureChange] inited")
        except Exception as e:
            if isinstance(e, FileNotFoundError):
                logger.warn(f"[SD] init failed, {config_path} not found.")
            else:
                logger.warn("[SD] init failed.")
            raise e

    @staticmethod
    def get_config_path(json_path: str):
        curdir = os.path.dirname(__file__)
        return os.path.join(curdir, json_path)

    @staticmethod
    def update_config(config_path, user_id, append):
        
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        if append:
            config["use_group"].append(user_id)
        else:
            config["use_group"].remove(user_id)
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)

    def handle_image_mode(self, content, e_context):
        context = e_context['context']
        if content == "开启图生图":
            if context["msg"].other_user_id not in self.other_user_id:
                self.other_user_id.append(context["msg"].other_user_id)
                config_path = self.get_config_path("config.json")
                self.update_config(config_path, context["msg"].other_user_id, append=True)
                replyText = "🥰图生图模式已开启，请发送图片给我,我将为您进行图像处理"
            else:
                replyText = "🤖图生图模式已开启，请勿重复开启"
            MessageReply.reply_Text_Message(True, replyText, e_context)

        elif content == "关闭图生图":
            if context["msg"].other_user_id in self.other_user_id:
                self.other_user_id.remove(context["msg"].other_user_id)
                config_path = self.get_config_path("config.json")
                self.update_config(config_path, context["msg"].other_user_id, append=True)
                replyText = "🥰图生图模式已关闭"
            else:
                replyText = "😭请检查图生图是否开启"
            MessageReply.reply_Text_Message(True, replyText, e_context)

    def on_handle_context(self, e_context: EventContext):
        if not self.use_pictureChange:
            replyText = f"😭图生图关闭了，快联系管理员开启图生图吧🥰🥰🥰"
            MessageReply.reply_Text_Message(False, replyText, e_context)
            return


        channel = e_context['channel']
        if ReplyType.IMAGE in channel.NOT_SUPPORT_REPLYTYPE:
            return

        # 初始化消息
        context = e_context['context']
        context.get("msg").prepare()
        content = context.content.strip()

        print(context)
        sender_id = e_context.econtext["context"]["receiver"]

        # 认证管理员
        if content.startswith("认证"):
            # 假设认证管理员的信息应该是:"认证 root"
            # 分离参数
            content1 = content.split(" ")
            if content1 is None or len(content1) != 2:
                return
            if self.admin.verify_admin(sender_id, content1[1]):
                replyText = "🥰认证成功"
            else:
                replyText = "😭认证失败,请重新认证"
            MessageReply.reply_Text_Message(True, replyText, e_context)
            return

        if content.startswith("修改port"):
            content1 = content.split(" ")
            if len(content1) != 2:
                return
            self.admin.update_json(sender_id, "start", "port", value=content1[1])
            self.port = content1[1]
            replyText = f"🥰修改port成功，当前port为{self.port}"
            MessageReply.reply_Text_Message(True, replyText, e_context)
            return


        if content.startswith("修改密码"):
            content1 = content.split(" ")
            if content1 is None or len(content1) != 2:
                return
            self.admin.update_password(sender_id, content1[1])
            replyText = f"🥰修改密码成功"
            MessageReply.reply_Text_Message(True, replyText, e_context)

            return

        if content.startswith("修改host"):
            content1 = content.split(" ")
            if len(content1) != 2:
                return
            self.admin.update_json(sender_id, "start", "host", value=content1[1])
            self.host = content1[1]
            replyText = f"🥰修改host成功，当前host为{self.host}"
            MessageReply.reply_Text_Message(True, replyText, e_context)
            return

        # 清空管理员
        if content.startswith("清空管理员"):
            self.admin.clear_admin(sender_id)
            replyText = "🥰清空管理员成功"
            MessageReply.reply_Text_Message(True, replyText, e_context)
            return

        # 初始化画图参数
        check_exist = False
        denoising_strength = 0
        cfg_scale = 0
        prompt = ""
        negative_prompt = self.negative_prompt
        roleRule_options = {}

        # 初始化消息类型
        is_group = context["msg"].is_group
        request_bot_name = self.is_group_bot_name if is_group else self.single_bot_name

        # 测试
        logger.debug(context)
        logger.debug(f"收到信息：{content}")

        title = ""
        # 是否存在自定义规则
        for role in self.role_options:
            if content.startswith(role['title'] + " "):
                title = role['title']
                denoising_strength = role['denoising_strength']
                cfg_scale = role['cfg_scale']
                prompt = role['prompt']
                negative_prompt = role['negative_prompt']
                if "options" in role:
                    for key in role["options"]:
                        roleRule_options[key] = role["options"][key]
                check_exist = True
                break

        # 开启插件，否则不能正常使用（这里可以添加限制）
        if content in ["开启图生图", "关闭图生图"]:
            if self.admin.is_admin(e_context.econtext["context"]["receiver"]) == False:
                replyText = "😭您没有权限开启或关闭图生图"
                MessageReply.reply_Text_Message(True, replyText, e_context)
                return

            self.handle_image_mode(content, e_context)

        # 判断成员已经开启插件，没有开启直接跳过
        elif context["msg"].other_user_id in self.other_user_id:
            try:
                # 判断消息类型
                if e_context['context'].type == ContextType.IMAGE:
                    Common.process_init_image(request_bot_name, self.role_options, e_context)

                elif e_context['context'].type == ContextType.FILE:
                    Common.process_file(self.openai_api_base, self.openai_api_key, self.file_recognize_model,
                                        self.file_recognize_prompt, e_context)

                elif any(ext in content for ext in ["jpg", "jpeg", "png", "gif", "webp"]) and (
                        content.startswith("http://") or content.startswith("https://")):
                    Common.process_init_image_url(request_bot_name, self.role_options, e_context)

                elif e_context['context'].type == ContextType.IMAGE_CREATE:
                    Common.process_image_create(self.is_use_fanyi, self.bot_prompt, self.rules, self.Model,
                                                request_bot_name, self.start_args, self.default_params,
                                                self.default_options, e_context)

                # 以下是对文字消息的操作
                elif content.startswith("⭐ 暂不处理 "):
                    file_content = content.split()[2]
                    logger.info(f"{file_content}")
                    replyText = "🥰图片已成功删除\n🧸感谢您的使用！"
                    # util.delete_file(file_content)
                    MessageReply.reply_Text_Message(True, replyText, e_context)

                elif content.startswith("🤖 图像修复 "):
                    Common.process_baidu_image(self.baidu_api_key, self.baidu_secret_key, e_context)

                elif content.startswith("🖼️ 图像描述 "):
                    Common.process_image(self.openai_api_base, self.openai_api_key, self.image_recognize_model,
                                         self.image_recognize_prompt, e_context)

                elif content.startswith("🎡 自定义 "):
                    message_limit = MessageLimit()
                    if message_limit.isLimit(self.max_number, e_context):
                        return
                    message_limit.using()
                    Common.process_image_custom(self.is_use_fanyi, self.bot_prompt, self.Model, request_bot_name,
                                                self.start_args, negative_prompt, self.max_size, e_context)
                    message_limit.success(self.max_number)

                # 判断用户发送的消息是否在config.json预设里面
                elif check_exist:
                    message_limit = MessageLimit()
                    if message_limit.isLimit(self.max_number, e_context):
                        return
                    message_limit.using()
                    Common.process_image_change(self.Model, request_bot_name, self.start_args, self.default_options,
                                                roleRule_options, denoising_strength, cfg_scale, prompt,
                                                negative_prompt, title, self.max_size, e_context)
                    message_limit.success(self.max_number)

                elif content.startswith("🎡 变换 "):
                    Common.process_image_transform(self.Model, request_bot_name, self.start_args, self.use_https,
                                                   self.host, self.port, self.file_url, prompt, negative_prompt,
                                                   self.max_size, e_context)

                elif content.startswith("🤖 放大 "):
                    Common.process_image_large(self.use_https, self.host, self.port, self.file_url, e_context)

                elif content.startswith("文生音 "):
                    prompt = content.replace("文生音 ", "")
                    logger.info(content)
                    Common.process_text_music(self.openai_api_base, self.openai_api_key, self.music_model,
                                              prompt, e_context)

                # 跳过插件，到下一个插件里面
                else:
                    e_context.action = EventAction.CONTINUE

            except Exception as e:
                replyText = "[😭SD画图失败] " + str(e) + "\n🧸快联系管理员解决问题吧！"
                logger.error("[SD画图失败] exception: %s" % e)
                MessageReply.reply_Error_Message(True, replyText, e_context)
                # util.delete_file(file_content)
        else:
            e_context.action = EventAction.CONTINUE

    def get_help_text(self, **kwargs):
        if not conf().get('image_create_prefix'):
            help_text = "画图功能未启用"
        else:
            trigger = conf()['image_create_prefix'][0]
            help_text = message_type.on_help_reply(trigger, self.rules)
        return help_text
