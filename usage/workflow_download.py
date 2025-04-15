from jmcomic import *
from jmcomic.cl import JmcomicUI

# 下方填入你要下载的本子的id，一行一个，每行的首尾可以有空白字符
jm_albums = '''
JM1014656
JM1125310
JM1120072
JM1115975
JM1113856
JM1112278
JM650124
JM1107430
JM1100966
JM1097335
JM1094997
JM1091272
JM1090197
JM1090194
JM1085900
JM1085769
JM1084413
JM1080609
JM639407
JM1079732
JM1079387
JM1076883
JM1076141
JM1075785
JM1075206
JM1072265
JM1071939
JM1071320
JM1062577
JM1063145
JM1062571
JM1062110
JM1054176
JM1054172
JM1053385
JM1052034
JM1047110
JM1047100
JM1044048
JM1042357
JM1041867
JM1040803
JM1038767
JM1038510
JM1037713
JM1034420
JM1034018
JM1033440
JM1033181
JM1030112
JM1029514
JM1028368
JM1028153
JM1025558
JM1025545
JM1025543
JM1025317
JM1023165
JM1023164
JM1022658
JM1022259
JM1021771
JM1020306
JM1020305
JM1019816
JM1015385
JM1015383
JM1015020
JM1015019
JM1014655
JM649704
JM649662
JM649532
JM643932
JM643919
JM642196
JM642193
JM636711
JM636127
JM635890
JM632541
JM632091
JM631044
JM631038
JM627978
JM614677
JM613012
JM613008
JM612863
JM612857
JM612856
JM612855
JM612854
JM612853
JM612852
JM612851
JM612850
JM612849
JM612848
JM612847
JM612730
JM605689






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
