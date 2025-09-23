from jmcomic import *
from jmcomic.cl import JmcomicUI

# 下方填入你要下载的本子的id，一行一个，每行的首尾可以有空白字符
jm_albums = '''
 JM1213183
 JM1207964
 JM1201036
 JM1201032
JM1198346
 JM1026066
 JM1162594
JM1169679
 JM1152984
 JM1152982
 JM1141306
 JM1152145
 JM1100966
 JM1201423
 JM1068578
JM1075206
JM1072265
 JM639407
 JM1071320
 JM1062577
 JM1062571
 JM1054172
JM1038510
JM1037713
JM1034420
 JM1041867
 JM1033440
JM1029514
JM1028368
 JM1025545
 JM1025543
 JM1023165
 JM1023164
 JM1020305
JM1019816
JM1014655
JM649532
JM643919
JM632541
JM612853
JM605689
JM612851
 JM1211968
 JM1211150
 JM1210938
 JM1211037
 JM1212223
JM1211114
 JM1212119
 JM1213425
JM1211038
 JM1213669
JM1213642
JM1212268
 JM1211578
JM1211972
 JM1211540
 JM1211981
 JM1214424
JM1211562
 JM1212020
 JM1213051
JM1214303
 JM1211896
JM1212312
 JM1214289
 JM1214377
 JM1214511
 JM1211733
 JM1212979
 JM1212508
 JM1214551
 JM1212014
 JM1213763
 JM1212581
 JM1212557
 JM1213705
 JM1213535
 JM1212012
 JM1212236
 JM1213769
 JM1211809
 JM1214304
 JM1212588
 JM1213655
JM1213050
 JM1213254
JM1213043
JM1213422
 JM1212258
JM1213667
JM1212262
JM1214044
 JM1213258
JM1212978
 JM1211567
JM1213893
JM1212538
 JM1211214
 JM1212640
JM1212411
JM1211566
 JM1211898
 JM1213252
 JM1213096
 JM1214394
 JM1211576
 JM1214393
JM1213424
JM1213753
JM1213662
 JM1213888
 JM1213930
JM1211772
 JM1213675
JM1213251
JM1212529
 JM1212299
 JM1214068
 JM1213148
JM1210977
 JM1214436
JM1213127
 JM1214741
JM1211806
 JM1213442
 JM1211935
 JM1214430
JM1213302
JM1213805
 JM1212026
JM1211477
 JM1212536
JM1214217
 JM1210909
JM1213664
 JM1212897
 JM1211905
 JM1213797
 JM1214064











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
