from jmcomic import *
from jmcomic.cl import JmcomicUI

# 下方填入你要下载的本子的id，一行一个，每行的首尾可以有空白字符
jm_albums = '''
     JM1240398
JM1240667
 JM1240519
 JM1239715
 JM1239224
 JM1239197
 JM1239122
 JM1239141
 JM1238358
 JM1238371
JM1238350
JM1237970
JM1237904
JM1237236
 JM1243875
JM1228372
JM1160211
JM1071192
 JM1023569
 JM1018595
 JM1018585
 JM499796
 JM1237049
 JM1237042
 JM1235904
 JM1235979
JM1235659
JM1235627
 JM1235472
 JM1235489
 JM1235329
JM1235317
 JM1235403
 JM1233596
 JM1234081
JM1234078
 JM1234079
 JM1233946
 JM1233949
 JM1233557
 JM1233548
 JM1233555
 JM1233529
 JM1233307
 JM1233027
 JM1232509
JM1232422
 JM1232037
 JM1231957
JM1231771
 JM1230984
JM1230612
 JM1230375
 JM1230355
 JM1230057
 JM1230058
 JM1230066
 JM1230049
 JM1230051
 JM1229893
 JM1230018
 JM1229649
 JM1229440
 JM1229356
 JM1229445
 JM1229302
 JM1229333
 JM1228852
 JM1228931
JM1228710
 JM1228564
JM1228451
 JM1228431
JM1228279
 JM1228184
 JM1227844
JM1227855
 JM1227694
 JM1227724
 JM1227680
 JM1227485
 JM1227608
 JM1227374
 JM1226817
 JM1226871
 JM1226767
JM1226740
JM1226726
 JM1226729
 JM1226537
JM1226436
 JM1226098
 JM1226103
 JM1226083
 JM1225818
 JM1225799
 JM1225724
 JM1225329
















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
