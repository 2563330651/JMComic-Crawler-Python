from jmcomic import *
from jmcomic.cl import JmcomicUI

# 下方填入你要下载的本子的id，一行一个，每行的首尾可以有空白字符
jm_albums = '''
    JM1215253
JM1215913
JM1195504
JM1027519
JM1470691
JM1434352
JM1231531
JM1471114
JM1450456
JM1468138
JM1473367
JM1451739
JM1467751
JM1471525
JM1473352
JM1468571
JM1472554
JM129895
JM1471547
JM1469189
JM1469281
JM1472462
JM1469238
JM1469590
JM1470097
JM1469012
JM1470774
JM1471991
JM1471989
JM1471590
JM1471577
JM1473061
JM1469382
JM1471990
JM1468129
JM1470246
JM1444361
JM1435180
JM1416592
JM1242056
JM1221889
JM1241795
JM1210482
JM1210483
JM1204570
JM1205024
JM1126221
JM1051135
JM558109
JM557755
JM548234
JM388968
JM393479
JM399115
JM387616
JM1455264
JM1466736
JM1467093
JM1421898
JM1209098
JM1421897
JM1256417
JM1472170
JM1470550
JM1474484
JM1472715
JM1468159
JM1468684
JM1469576
JM1469650
JM1468555
JM1468134
JM1475347
JM1472773
JM1475274
JM1469263
JM1468133
JM1474997
JM1474997
JM1475342
JM1469854
JM1468650
JM1472369
JM1471718
JM1472086
JM1469276
JM1470548
JM1469725
JM1470441
JM1475298
JM1473359
JM1467756
JM1469287
JM1471572
JM1472740
JM1472710
JM1474349
JM1474986
JM1468683
JM1471596
JM1470495
JM1469309
JM1469775
JM1469557
JM1475661
JM1474281
JM1475002
JM1243007
JM1022415
JM1474960
JM1468934
JM1474687
JM1474687
JM1472333
JM1473983
JM1476011
JM1475990
JM1471115
JM1468614
JM1469806






















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
