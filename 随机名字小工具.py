import string
import sys
import random
import threading
import os
from pathlib import Path

from PyQt6.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLineEdit, QComboBox, QLabel, QPushButton

hanzi = "一,乙,二,十,丁,厂,匕,乃,卜,人,入八,九,几,了,力,乃,刀,又,三,于,干,亏,士,工,土,才,寸下,大丈,与,万,上,小,口,巾,山,千,乞,川,亿,个,勺,久,凡,及,夕,丸,么,广亡,门,义,之,尸,弓,已,己,子,卫,也,女,飞,刃,习,叉,马,乡,丰,王,井,开,夫,天,无,元,专云,扎,艺,木,五,支,厅,不,太,犬,区,历,友,匹,车,巨,牙,屯,比,互,切,瓦,止,少,日,中,冈,贝,内,水,见,午,牛,手毛,气,升,长,仁,什,片,仆化,仇,币,仍,仅,斤,爪,反,介父,从,今,凶,分,乏,公,仓,月,氏,勿,欠,风,丹,匀,乌,凤,勾文,六,方,火,为,斗,忆,订,计,户,认,心尺,引丑,巴,孔,队,办,以,允,予,劝,双,书,幻,玉,子,刊,示,末,未,击,打,巧正,扑扒,功,仍,去,甘,世,古,节,本,术,可,丙,右,左,厉,石,布,龙,平,灭,轧,东,卡,北,占,业,旧,帅,归,且,旦,目叶,甲,申,叮,电,号,田,由,史,只,央,兄,叼,叫,另,叨,叹,四,生,失,禾,丘,付,仗,代,仙,们,仪,白,仔,他,斥,瓜,乎丛,令,用,甩,印,乐,句,匆,册,犯,外,处,冬,鸟,务,包,饥,主,市,立,闪,兰,半,汁,汇,头,汉,宁,穴,讨,写,让,礼,训必,议,讯,记,永,司,尼,民,出,辽,奶,奴,加,召,皮,边,发,孕,圣,对台,纠,母,幼丝,式,刑,动,扛,寺,吉,扣,考,托老,执巩,圾,扩,扫,地,场,耳,共,芒,亚,芝,朽,朴,机,权,过,臣,再,协,西,压,厌,在,有,百,存,而,页,匠,夸,夺,灰达,列,死,成,夹,轨,邪,划迈,至,此,贞,师,尘,尖,劣,当,早,吐,吓,虫,曲,团,同,吊,吃,因,吸,吗,屿,帆,岁,回,岂刚,则,肉,网,年,朱,先,丢,舌,竹,迁,乔,伟,传乒,乓,休,伍,伏,优,延,任,伤,份,华,仰,仿,伙,自,血,问,似,后,行舟,全,会,杀,兆,企,众,爷,伞,创,肌,朵,杂,危,旬,旨,负,各,名,多争,色,壮,冲,冰,庄,庆,亦,刘,齐,交,次,衣,产决,充,妄,闭,问,闯,羊,并,关,米,灯,州,汗,污,江,池,汤,忙,兴,宇,守,宅,安,农,讲,许论,讽,设,访,军,寻,那,迅尽,导,孙,阵,阳,收,价,阴,防,奸,如,妇,好,她,妈,戏,羽,观,欢,买,红,纤,级,约,纪,驰,巡,伐,画,寿,弄,麦,形,进,戒,远,违,运扶,抚坛,技,坏,扰,拒,找,批,扯,址,走,抄,坝,贡,攻,赤,折,抓,扮,抢,抛,投,抗,护,扭,孝,均,坟,坑,坊,抖,壳,志块,声,把,报,却,芽,花,芹芬,苍,芳,严,芦,劳,克,苏,杆,杠,杜,材,村,杏,极,李,杨,求,更,束,豆,两,丽,医,辰,励,否,还,歼,来,连,步,坚,早,盯,时,吴,助,县,里,呆,园,旷,围,呀,吨,足,邮男,困,吵,串,员,听,吩,吹,呜,吧,吼,别岗,帐,财,针,钉,告,我,乱,利,秃,秀,私,每,兵,估,体,何,但,伸,作,伯,伶,佣,低,你,住,位,伴,身,皂,佛,近,彻,役余,希,坐,谷,含,邻,岔,肝,龟,免,狂,犹,角,删,条,卵,岛,迎,饭,饮,系,言,冻,状,亩,况,床,疗,应,冷,这,序,辛,弃,治,忘,闲,闷,判,灶,弟,汪,沙,汽,沃,泛,沟,没,沉,沈,怀,忧,快,完,宋,宏,牢,究,穷,灾,良,证,评,启,补,社,识诉,诊,词,译,君,灵,即层,尿,尾,迟,局,改,张,忌,际,陆,阿,陈,阻,附,妙,妖,妨,努,忍,劲,鸡,驱,纯,纱,纳,纲,驳纵,纷,纸,纹,纺,纽,驴,奉,玩,环,武,青,责,现,表,规,抹,扰,拔,拣,担,押,抽,拐,拖,拍,者,顶,拆,拥,抵,抱,势,垃,拉,拦,拌,幸,招,坡,披拨,择,抬,其,取,苦,若,茂,苹,苗,英,范,直,茄,茎,茅,林,枝,杯,柜,析,松,构,枪,杰述,枕,丧,或,画,卧,事,刺,枣雨,卖,矿,码,厕,奔,奇,奋,态,欧,垄,妻,轰,顷,转,斩,轮,到,非,叔,肯,齿,软,些,虎,虏,贤,肾,尚,旺,具果,味,昆国,昌,畅,明,易,昂,典,固,忠,咐,呼,鸣,咏,呢,岸,岩,帖,罗,帜,岭,凯,败,购,图,钓,制,知,垂,物,乖,刮,秆,和,季委,佳,侍供,使,例,版,侄,侦,侧,凭,侨,货,依,的,迫,质,欣,征,往,爬,彼,径,所,舍,命,金,斧,爸,采,受,乳,贪,念,贫,肤,肺,肢,胀,朋,股,肥,胁,周,昏,鱼,兔,狐,忽,狗,备,饰,饱,饲,变,京,享,店,夜,庙,府,底,剂,郊,废,净,盲,放刻,育,闸,闹,郑,券,卷,单,炒,炊,炕,炉,沫,浅,法泄,河,沾,泪,泊,沿,泡,注,泥,波,泼,泽,治,怖,性,怕,怜,怪,学宝,宗,定,宜,审,宙,官,空,实,试,郎,诗,肩,房,诚,衬,衫,视,话,诞,询,该,详,建,肃,录,隶,居,庙,刷,屈,弦,承,孟孤,陕,降,,限,妹,姑,姐,姓,始,驾,参,艰,线,练,组,细,驶,织,终,驻,骆,绍,经,贯,奏,春,帮,珍,玻,毒,型,挂,封,持,项,垮,挎,城,挠,政,赴,赵,挡,挺,括,拴,拾,挑,指,垫,挣,挤,拼,挖,按,挥,挪,某,甚,革,荐,巷,带,草,茧,茶,荒茫,荣,荡,故,胡,南,药,标,枯,柄,栋,相,柏,柳,柱,柿,栏,树,要,咸,威,歪,研,砖,厘,厚,砌,砍,面,耐,耍,牵,残,殃轻,鸦,皆,背,战,点,临,览,竖,省,削,尝,是,盼眨,哄,显,冒,映,星,昨,畏,胃,贵,界,虹,虾,恩,蚂,虽,品,咽,骂,哗咱,响,哈,咬,哪,咳,炭,峡,罚,贱,贴,骨,钞,钟,钢,钥,钩,卸,缸,拜看,矩,怎,牲,选,适,秒,香,种,科,重,复,竿,段便,贷,顺,修,保,促,侮,俭,谷,俘,信,皇,泉,鬼,侵,追,俊,盾,待,律,很,须,叙,剑,逃,食盆,胆,胜,胞,胖,脉,勉,狭,狮,独,狡,狱,狠,贸,怨,饶,蚀,饼,饺,弯,将,哀,亭,亮,度,迹,庭,疯,疫,疤,姿,态,亲,音,帝,施,闻,阀,阁,差,养,美,姜,叛,送,类,迷,前,首,逆,总,炼,炸,炮,烂,剃,洁,洪,洒,浇,浊,洞,测,派,洽,染,济,洋,洲,浑,浓,津,恒,恢,恰,恼恨,举,觉,宣室,宫,宪,突,穿,窃,客,冠,军,语,扁,袄,祖,神,祝,误,诱,说,诵,垦,退,既,屋,昼,费,陡,眉,孩,除,险,院,娃,姥,姨,姻,娇,怒,架,贺,盈,勇,怠,柔,垒,骄,骆,绑,绒,结,绕,绘,给,络,绝,绞,统,蚁,耕,耗,艳,泰,珠,班,素,蚕,顽,盏,匪,捞,栽,捕,振,载,赶,起盐,捎,捏,埋,捉,捆,捐,损,捡,换,挽,挨,热,都,哲,逝,恐,壶,耻,耽,恭,莲,莫,荷,获晋,恶,真,框,桂,档,桐,株,桥桃,格,校,核,样,根,索,哥,速,逗,栗,配,翅,辱,唇,夏,础,破,原,套,逐,烈,殊,顾,轿,较,顿,毙,致,柴,桌虑,监,紧党,晒,晓,鸭,晃,晌,晕,蚊,哨,哭,恩,唤,啊,唉,罢,峰,圆,贿,贼,钱,钳,钻,铁,铃,铅,缺,氧,特,牲,造,乘,敌,秤,租秧,秩,称秘,透,笔,笑,债,笋,借,值,倚,倾,倒,倘,俱,倡,候,倍,俯,倦,健,臭,射,躬,息,徒,徐,舱,般,航,途,拿,爹爱,颂,翁,胸,胳,脏,胶,脑,狸,狼,逢,留,皱,饿,恋,桨,浆,衰,高,席,准,座,脊,症,疾,疼,疲,效,离,唐,资,凉,站,剖,,竞,部,旁,旅,畜,阅,羞,瓶,拳,粉,料,益,烤,烘,烦,烧,烛,烟,递,涛,渐,涝,酒,涉,消,浩,海,涂,浴,浮,流,润,浪,浸涨,烫,涌,悟,悄,悔,悦,害,宽,家,宵,宴,窄,宰,案,请,诸,读,课,谁,谈调,谅,谊,朗,扇,袜,袖,袍,被,详,冤,剥,恳展,剧,悄,弱,陵,陶,陷,陪,娱,娘,通,能,难,预,桑,绢,绣,继,捆,挂朗,球,理,堆堵,捧,描,域,掩,捷,排,掉,推,掀,授,掏,掠,接,控,探,据,掘,培,教,职,基,著,勒,黄,萌,萝,菌,菜,萄,萍,菠,营,械,梦,梢,梅,检,梳,梯桶,救,副,票,戚,爽,聋,袭,盛雪,辅,辆,虚,雀,堂,常,匙,晨,睁,眯,眼,悬,野,啦,晚,啄,距,跃,略,蛇,累,唱,患,唯,崖,崭,崇,圈,铜,铲银,甜,梨犁,移,笨,笼,笛,符,第,敏,做,袋,悠,偿,偶,偷,您,售,停,偏,假,得,衔,盘,船,斜,盒,鸽,悉,欲,彩,领,脚,脖,脸,脱,象,够,猜,猪,猎,猛,馅,馆,凑,减,毫,麻,痒,痕,廊,康,庸,鹿,盗,章,竟,商,族,旋,望,率,着,盖,粘,粗,粒,斯,剪,兽清,添,淋,淹,渠,渐,混,渔,淘波,淡,深,婆,梁,渗,情,惜,惭,悼,惧,惕,,惊,惨,惯,冠寄,宿,窑,密,谋,谎,祸,谜,逮,敢,屠,弹,随,蛋,隆,隐,婚,婶,颈,骑,绩,绪,续,维,绸,绿,描,琴,斑,替,款,堪,搭,塔,越,趁,趋,超,提,堤,搏,揭,喜,揪,搜,煮,援裁,搁,搂,搅,握,揉,斯,欺,联,散,惹,葬,葛,董,萄,敬,葱,落,朝,辜,葵,棒,棋,植,森,椅,椒,棵,棍,棉,棚,棕,惠,惑,逼,厨,厦,硬,确,雁,殖,裂,雄,暂,雅,辈,悲,紫,辉,敞,掌,赏,晴,暑,最,量,喷晶,喇,遇,喊,景,践,跌,跑,遗,蛙,蛛,蜓,喝,喘,喉,幅,帽,赌,赔,黑,铸,铺,链,销,锁,锄,锅,锈,锋,锐,短,智,毯,鹅,刺,稍,程,稀,税,筐,等,筑,策,筛,筒,答,筋,筝,傲,傅,牌,堡,集,焦,傍,储,奥,衔,御,彻,循,艇,舒,番,释,禽,腊,脾腔,鲁,猾,猴,然,谗,装,就,痛,童,阔,善,羡,普,粪,尊,道,曾,焰,港,湖,渣,温,渴,滑,湾,渡,游,滋,溉,愤,愧,愉,慨割寒,富,窜,窝,窗,遍,裕,裤,裙,谢,谣,谦,属,屡,强,,粥,疏,隔,隙,絮,嫂,登,骗,缎缓,编,缘,期,释,瑞,魂,肆,摄,摸,填,搏,塌,鼓,摆,携,搬,摇,搞,塘,摊,蒜,勤鹊,蓝,墓,幕,蓬,蒸,献,禁,楚,想,槐,楼,概,赖,酬,感,碍,碑,碎,碰,碗,雷,零,雾,雹输,督,龄,睛,睡,睬,鄙,愚,暖盟,歇,暗,照,跨,跳,跪,路,跟,遣,蛾,蜂,嗓,置,罪,罩,错,锡,锣,锤,锦,键,锯,矮,辞,稠,愁,筹,签,毁,舅,鼠,催,傻,像,躲,微,愈,遥,腰,腥,腹,腾,腿,触,解,酱,痰,谦,新,韵,意,粮,数,煎,塑,慈,煤,煌,满,漠,源,滤,滥,滔,溪,溜,游滚,滨,梁慎,誉,塞,谨,福,群,殿,辟,障,嫌,嫁,叠,缝,缠,静,碧,璃,墙,撇,嘉,摧,截,誓,境,摘,摔,聚,蔽,慕,暮,蔑,模榴,榜,榨,歌,遭,酷,酿,酸,磁,愿,需,弊,裳,颗,嗽,蜓,蜡,蝇,蜘,赚,锹,锻,舞,稳,算箩,管,僚,鼻,魄,貌,膜,膊,膀鲜,疑,馒,裹,敲,豪,膏,遮,腐,瘦,辣,竭,端,旗,精,歉,熄,熔,漆,漂,漫,滴,演,漏,慢,寨,赛,察,蜜,谱,嫩翠,熊,凳,骡,缩,慧,撕,撒趣,趟,撑,播,撞,撤,增,聪,鞋,蕉,蔬,横,槽,樱,橡,飘,醋,嘴,震,霉,瞒,题,暴,瞎,影,踢,踏,踪,蝴,蝶,瞩,墨,镇,靠,稻,黎,稿,箱,箭,篇僵,躺,僻,德,艘,膝,膛,熟,摩颜,毅,糊,遵,潜,潮,懂,额,慰,劈,操,燕,薯,薪,薄,颠,橘,整,融餐,嘴,蹄,器,赠,默,镜,赞,篮,邀,衡膨,雕,磨,凝,辨,辩,糖,糕,燃,澡,激,懒,壁,避缴,戴,擦,鞠藏,霜,霞,瞧,蹈,螺,穗,繁,辫,赢,糟,糠,燥,臂,翼,骤,鞭,覆,蹦,镰,翻,鹰,警,攀,蹲,颤,瓣,爆,疆,壤,耀,躁,嚼,嚷,籍,魔,灌,蠢,霸,露,囊,罐"
def write_file(content):
    # 定义文件路径，这里假设文件位于桌面上，文件名是 "example.txt"
    desktop_path = Path(os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop'))
    file_path = desktop_path / 'name_file.txt'

    # 检查文件是否存在
    if not file_path.exists():
        # 文件不存在，创建文件并写入内容
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
    else:
        # 文件存在，覆盖内容
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)

    print(f"文件 '{file_path}' 已处理。")
def zhuijia(congtent):
    import os

    # 定义文件路径，这里假设桌面路径在Windows和macOS上有所不同
    desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']),
                                'Desktop') if os.name == 'nt' else os.path.join(os.path.expanduser('~'), 'Desktop')
    file_path = os.path.join('zong.txt')

    # 要写入或追加的内容
    content_to_write = congtent+"\n"

    # 检查文件是否存在
    if os.path.exists(file_path):
        # 文件存在，以追加模式打开文件
        with open(file_path, 'a', encoding='utf-8') as file:
            file.write(content_to_write)
    else:
        # 文件不存在，以写入模式创建文件
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content_to_write)

    print(f"操作完成，文件路径：{file_path}")

file_content = ""
def is_string_in_file():
    global file_content
    """
    检查一个字符串是否存在于文件中。

    :param file_path: 文件的路径
    :param search_string: 要搜索的字符串
    :return: 如果字符串存在于文件中，则返回True；否则返回False
    """
    try:
        with open("zong.txt", 'r', encoding='utf-8') as file:
            # 读取文件的所有内容
            file_content = file.read()
            # 检查字符串是否在文件内容中
    except FileNotFoundError:
        # 如果文件不存在，可以打印一个错误消息或进行其他处理
        with open("zong.txt", 'w', encoding="utf-8") as file:
            file.write("asd"+"/n")
            file.write("asd" + "/n")
            file.write("asd" + "/n")
            file.write("asd" + "/n")
            file.write("asd" + "/n")
            file.write("asd" + "/n")
            file.write("asd" + "/n")
            file.write("asd" + "/n")
            file.write("asd" + "/n")
        return False
    except Exception as e:
        # 处理其他可能的异常
        return False
class MyApp(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        # 设置窗口标题和大小
        self.setWindowTitle('随机名字小工具')
        self.setGeometry(100, 100, 300, 60)

        # 创建主垂直布局
        main_layout = QVBoxLayout()

        # 创建水平布局来放置三组文本输入框和下拉选择框
        row_layout = QHBoxLayout()

        # 创建第一组文本输入框和下拉选择框
        self.text_input1 = QLineEdit(self)
        self.text_input1.setText("3")
        self.combo_box1 = QComboBox(self)
        self.combo_box1.addItem('汉字')
        self.combo_box1.addItem('字母')
        self.combo_box1.addItem('数字')
        row_layout.addWidget(self.text_input1)
        row_layout.addWidget(self.combo_box1)

        # 创建第二组文本输入框和下拉选择框
        self.text_input2 = QLineEdit(self)
        self.text_input2.setText("3")
        self.combo_box2 = QComboBox(self)
        self.combo_box2.addItem('字母')
        self.combo_box2.addItem('汉字')
        self.combo_box2.addItem('数字')
        row_layout.addWidget(self.text_input2)
        row_layout.addWidget(self.combo_box2)

        # 创建第三组文本输入框和下拉选择框
        self.text_input3 = QLineEdit(self)
        self.text_input3.setText("3")
        self.combo_box3 = QComboBox(self)
        self.combo_box3.addItem('数字')
        self.combo_box3.addItem('字母')
        self.combo_box3.addItem('汉字')
        row_layout.addWidget(self.text_input3)
        row_layout.addWidget(self.combo_box3)

        # 将水平布局添加到主垂直布局中
        main_layout.addLayout(row_layout)

        # 可选：添加一个按钮来触发操作
        self.execute_button = QPushButton('执行', self)
        self.execute_button.clicked.connect(self.on_execute_clicked)
        main_layout.addWidget(self.execute_button)

        # 可选：添加一个标签来显示输出（可选）
        self.output_label = QLabel(self)
        main_layout.addWidget(self.output_label)

        # 设置布局
        self.setLayout(main_layout)

    def on_execute_clicked(self):
        texts = [self.text_input1.text(), self.text_input2.text(), self.text_input3.text()]
        options = [self.combo_box1.currentText(), self.combo_box2.currentText(), self.combo_box3.currentText()]
        # 获取所有文本输入框和下拉选择框的内容
        thread = threading.Thread(target=self.yewu,args=())
        thread.start()


        # 更新标签内容（可选）
        output_str = '\n'.join(f'组合 {i}: 选择项: {option}, 输入内容: {text}' for i, (option, text) in enumerate(zip(options, texts), 1))
        self.output_label.setText(output_str)
    def yewu(self):
        global file_content
        texts = [self.text_input1.text(), self.text_input2.text(), self.text_input3.text()]
        options = [self.combo_box1.currentText(), self.combo_box2.currentText(), self.combo_box3.currentText()]
        wai_zong = 0
        zong_zong = ""
        while (wai_zong < 1000):
            wai_zong+=1
            zong = ""
            # 打印输出或进行其他处理
            for i, (text, option) in enumerate(zip(texts, options), 1):
                hanzi_mm = ""
                shuzi = ""
                if (option == "汉字"):
                    hanzi_list = hanzi.split(',')
                    # 从列表中随机选择三个不同的汉字
                    random_hanzi = random.sample(hanzi_list, int(text))
                    # 打印结果
                    for temp in random_hanzi:
                        hanzi_mm = hanzi_mm + temp
                    hanzi_mm = hanzi_mm[0:int(text)]
                    zong = zong + hanzi_mm
                if (option == "字母"):
                    lowercase_letters = list(string.ascii_lowercase)  # 只包含小写字母
                    random_lowercase_letters = random.sample(lowercase_letters, int(text))
                    random_lowercase_letters_str = ''.join(random_lowercase_letters)
                    random_lowercase_letters_str = random_lowercase_letters_str[0:int(text)]
                    zong = zong + random_lowercase_letters_str
                if (option == "数字"):
                    random_numbers = random.sample(range(0, 10), int(text))
                    # 打印结果
                    for temp in random_numbers:
                        shuzi = str(shuzi) + str(temp)
                    shuzi = shuzi[0:int(text)]
                    zong = zong + shuzi
            if(len(file_content)<6):
                is_string_in_file()
            else:
                if(zong in file_content):
                    print("去掉")
                else:
                    if(zong_zong == ""):
                        zong_zong = zong
                    else:
                        zong_zong = zong_zong + "\n"+zong
        print(zong_zong.strip())
        write_file(zong_zong)
        zhuijia(zong_zong)
# 创建应用程序对象
app = QApplication(sys.argv)

# 创建窗口对象
window = MyApp()
window.show()

# 运行应用程序主循环
sys.exit(app.exec())