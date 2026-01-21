from jmcomic import *
from jmcomic.cl import JmcomicUI

# 下方填入你要下载的本子的id，一行一个，每行的首尾可以有空白字符
jm_albums = '''
    JM1148430
 JM564065
 JM1131361
 JM561741
JM1126650
 JM1123445
 JM488736
 JM1060291
 JM374030
 JM1113209
 JM1103680
 JM1094079
 JM1099437
 JM1079316
 JM1078959
 JM1078893
 JM1078270
 JM1076637
JM1076271
 JM1072262
 JM1071456
 JM1068575
 JM1061317
 JM1060791
JM1055649
 JM1053398
 JM1034270
 JM1030625
 JM1027667
 JM1073935
 JM1027653
 JM1025496
 JM1026830
 JM1025344
 JM1024944
 JM1023190
 JM1021468
 JM1021117
 JM1017290
 JM1015036
 JM644970
 JM579799
 JM541135
 JM483831
 JM483832
 JM401840
 JM345766
 JM254738
 JM249756
 JM98509
 JM98648
 JM95024
 JM88399
 JM88398
 JM83461
 JM74378
JM46494
JM41663
 JM40443
 JM41243
 JM9782
 JM649406
 JM648246
JM649399
 JM647912
 JM646992
JM643150
JM640521
JM640249
 JM630364
JM628420
 JM627921
 JM612812
 JM620160
 JM611856
 JM611627
JM598473
 JM595982
 JM596941
JM575622
 JM1216231
 JM414379
 JM413876
 JM188965
JM189221
 JM149385
 JM1230746
JM1221466
JM1194921
 JM1133213
 JM1052934
 JM605738
 JM623172
 JM496445
JM485030
 JM477102
 JM360017
JM350269
 JM568473
 JM566741
 JM566552





















'''

# 单独下载章节
jm_photos = '''



'''


def env(name, default, trim=('[]', '""', "''")):
    import os
    value = os.getenv(name, None)
    if value is None or value == '':
        return default

    for pair in trim:
        if value.startswith(pair[0]) and value.endswith(pair[1]):
            value = value[1:-1]

    return value


def get_id_set(env_name, given):
    aid_set = set()
    for text in [
        given,
        (env(env_name, '')).replace('-', '\n'),
    ]:
        aid_set.update(str_to_set(text))

    return aid_set


def main():
    album_id_set = get_id_set('JM_ALBUM_IDS', jm_albums)
    photo_id_set = get_id_set('JM_PHOTO_IDS', jm_photos)

    helper = JmcomicUI()
    helper.album_id_list = list(album_id_set)
    helper.photo_id_list = list(photo_id_set)

    option = get_option()
    helper.run(option)
    option.call_all_plugin('after_download')


def get_option():
    # 读取 option 配置文件
    option = create_option(os.path.abspath(os.path.join(__file__, '../../assets/option/option_workflow_download.yml')))

    # 支持工作流覆盖配置文件的配置
    cover_option_config(option)

    # 把请求错误的html下载到文件，方便GitHub Actions下载查看日志
    log_before_raise()

    return option


def cover_option_config(option: JmOption):
    dir_rule = env('DIR_RULE', None)
    if dir_rule is not None:
        the_old = option.dir_rule
        the_new = DirRule(dir_rule, base_dir=the_old.base_dir)
        option.dir_rule = the_new

    impl = env('CLIENT_IMPL', None)
    if impl is not None:
        option.client.impl = impl

    suffix = env('IMAGE_SUFFIX', None)
    if suffix is not None:
        option.download.image.suffix = fix_suffix(suffix)


def log_before_raise():
    jm_download_dir = env('JM_DOWNLOAD_DIR', workspace())
    mkdir_if_not_exists(jm_download_dir)

    def decide_filepath(e):
        resp = e.context.get(ExceptionTool.CONTEXT_KEY_RESP, None)

        if resp is None:
            suffix = str(time_stamp())
        else:
            suffix = resp.url

        name = '-'.join(
            fix_windir_name(it)
            for it in [
                e.description,
                current_thread().name,
                suffix
            ]
        )

        path = f'{jm_download_dir}/【出错了】{name}.log'
        return path

    def exception_listener(e: JmcomicException):
        """
        异常监听器，实现了在 GitHub Actions 下，把请求错误的信息下载到文件，方便调试和通知使用者
        """
        # 决定要写入的文件路径
        path = decide_filepath(e)

        # 准备内容
        content = [
            str(type(e)),
            e.msg,
        ]
        for k, v in e.context.items():
            content.append(f'{k}: {v}')

        # resp.text
        resp = e.context.get(ExceptionTool.CONTEXT_KEY_RESP, None)
        if resp:
            content.append(f'响应文本: {resp.text}')

        # 写文件
        write_text(path, '\n'.join(content))

    JmModuleConfig.register_exception_listener(JmcomicException, exception_listener)


if __name__ == '__main__':
    main()
