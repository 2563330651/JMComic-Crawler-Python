from jmcomic import *
from jmcomic.cl import JmcomicUI

# 下方填入你要下载的本子的id，一行一个，每行的首尾可以有空白字符
jm_albums = '''
JM1127168
JM1127188
JM1127190
JM1127194
JM1127196
JM1127197
JM1126673
JM1126646
JM1126320
JM1126319
JM1126276
JM1125894
JM1125887
JM1126250
JM1126210
JM1126188
JM1125808
JM1126235
JM1071655
JM1125670
JM512399
JM1125607
JM1125605
JM1022045
JM1125307
JM1125073
JM1122532
JM513137
JM491482
JM1019738
JM1125231
JM1125226
JM1022027
JM1125214
JM598370
JM1125194
JM553019
JM1125063
JM480370
JM591947
JM1124934
JM1124931
JM1124925
JM1124893
JM1124888
JM1124879
JM1124861
JM1124859
JM1124857
JM1124590
JM1124350
JM1124269
JM1124348
JM488736
JM1124344
JM1124346
JM1123990
JM1123954
JM1123445
JM1123400
JM1123395
JM1123481
JM1121862
JM1123021
JM1123126
JM1122546
JM1122331
JM1122329
JM1122279
JM1122277
JM1121588
JM1121118
JM1121552
JM1121534
JM1121537
JM1121066
JM1120687
JM1120683
JM1120124
JM1120123
JM1120122
JM1119848
JM1118920
JM1119124
JM1118075
JM1118758
JM1118263
JM1118358
JM1117868
JM1117788
JM1117282
JM1116958
JM1116913
JM1116828
JM1114324
JM1115970
JM1115550
JM1114940
JM496555
JM1020532
JM1016715
JM1016191
JM1031102
JM1058163
JM1114784
JM1114801
JM1114797
JM466245



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
