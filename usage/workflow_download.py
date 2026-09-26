from jmcomic import *
from jmcomic.cl import JmcomicUI

# 下方填入你要下载的本子的id，一行一个，每行的首尾可以有空白字符
jm_albums = '''
    JM1467850
JM1472900
JM1470013
JM1475313
JM1472745
JM1472772
JM1469208
JM1472323
JM1468917
JM1472409
JM1476534
JM1469931
JM1474346
JM1475117
JM1472336
JM1470662
JM1469601
JM1473619
JM1469230
JM1472777
JM1470603
JM1470767
JM1469560
JM1468708
JM1475303
JM1472763
JM1471233
JM1472850
JM1476416
JM1474543
JM1469300
JM1472524
JM1473694
JM1475815
JM1468937
JM1469598
JM1468616
JM1468438
JM1472016
JM1472337
JM1470422
JM1469004
JM1469597
JM1474010
JM1476282
JM1474990
JM1475148
JM1469249
JM1472185
JM1472407
JM1470064
JM1468000
JM1470395
JM1470278
JM1472969
JM1471915
JM1475224
JM1474329
JM1467658
JM1474372
JM1470015
JM1475650
JM1474560
JM1468755
JM1468354
JM1474479
JM1473017
JM1470019
JM1473021
JM1470420
JM1469388
JM1474311
JM1468188
JM1468092
JM1474547
JM1474912
JM1469532
JM1473741
JM1469257
JM1468075
JM1468992
JM1472660
JM1474305
JM1470722
JM1475253
JM1471899
JM1475120
JM1467941
JM1470873
JM1472013
JM1469564
JM1474804
JM1474238
JM1474992
JM1470976
JM1472404
JM1468812
JM1473651
JM1474327
JM1467825
JM1475766
JM1474304
JM1474326
JM1472006
JM1472345
JM1468385
JM1469716
JM1469233
JM1469233
JM1030811
JM1441640
JM1236488
JM1248480
JM1248480
JM1447809























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
