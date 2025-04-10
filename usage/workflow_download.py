from jmcomic import *
from jmcomic.cl import JmcomicUI

# 下方填入你要下载的本子的id，一行一个，每行的首尾可以有空白字符
jm_albums = '''
JM1120109
JM1120618
JM1122271
JM1123140
JM1121534
JM1119855
JM1120110
JM1121586
JM1119533
JM1119997
JM1124548
JM1121589
JM1124922
JM1119846
JM1124521
JM1120046
JM1119889
JM1121862
JM1122566
JM1124505
JM1123126
JM1120595
JM1120045
JM1120739
JM1122284
JM1121047
JM1120146
JM1120022
JM1121143
JM1119841
JM1120122
JM1123956
JM1123398
JM1120614
JM1122290
JM1122278
JM1119536
JM1122591
JM1120615
JM1123386
JM1119843
JM1122307
JM1120632
JM1123492
JM1119124
JM1119873
JM1120145
JM1119844
JM1119894
JM1122362
JM1119899
JM1123385
JM1121588
JM1124229
JM1124245
JM1119847
JM1124526
JM1123031
JM1120616
JM1120622
JM1120708
JM1121567
JM1121050
JM1124349
JM1123030
JM1120119
JM1124589
JM1122282
JM1119683
JM1120679
JM1122246
JM1122286
JM1119595
JM1123037
JM1122311
JM1123390
JM1121833
JM1122725
JM1119697
JM1123044
JM1124522
JM1119151
JM1123929
JM1121068
JM1123050
JM1122550
JM1121590
JM1120600
JM1120621
JM1119681
JM1120611
JM1123954
JM1121553
JM1122251
JM1121066
JM1122287
JM1124501
JM1123923
JM1122338
JM1119880
JM1121594
JM1122552
JM1119115
JM1124270
JM1125054
JM1122277
JM1119848
JM1122546
JM1121093
JM1121118
JM1121537
JM1121049
JM1119908
JM1124247
JM1119877
JM1123021
JM1119157
JM1119902
JM1120601
JM1122534
JM1119128
JM1124248
JM1122275
JM1122554


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
