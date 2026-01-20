from jmcomic import *
from jmcomic.cl import JmcomicUI

# 下方填入你要下载的本子的id，一行一个，每行的首尾可以有空白字符
jm_albums = '''
    JM1249744
 JM1249731
 JM1249279
 JM1249739
 JM1249282
 JM1249290
JM1249333
 JM1249265
 JM1249195
JM1249728
JM1249198
 JM1249725
JM1249723
JM1249722
JM1249276
JM1249267
JM1249244
 JM1249240
 JM1249241
 JM1249196
 JM1249185
JM1249160
JM1249158
JM1249149
JM1249146
JM1249138
 JM1249063
JM1249061
 JM1249057
 JM1249054
 JM1249050
 JM1249047
JM1249048
 JM1249045
 JM1249041
JM1249035
 JM1249034
JM1249036
JM1249029
 JM1249032
 JM1249028
 JM1249027
JM1249023
JM1249020
 JM1249022
JM1249019
JM1249016
JM1021313
 JM1248981
JM1248889
 JM1248848
 JM1248851
 JM1248845
JM1248827
JM1248819
 JM1248816
JM1248807
 JM1248808
 JM1248803
JM1248804
 JM1248805
 JM1248797
JM1248801
 JM1248802
 JM1248783
JM1248778
JM1248774
JM1248772
 JM1248769
 JM1248770
JM1248764
JM1248761
 JM1248763
 JM1248756
JM1248649
JM1248647
 JM1248646
 JM1248645
JM1248610
 JM1248601
 JM1248567
JM1248563
 JM1248572
JM1248555
 JM1248544
 JM1248536
 JM1248538
 JM1248526
 JM1248531
JM1248524
JM1248522
 JM1248520
 JM1248515
 JM1248509
JM1248501
JM1248493
JM1248491
JM1248483
JM1248480
JM618075
 JM1020687
 JM1248380
JM1248371
JM1241157
JM1059530
 JM1164838
 JM1248278
 JM1248152
 JM1248248
 JM1248249
 JM1248250
JM1248172
 JM1248130
JM1248170
JM1248243
 JM1248174
JM1248158
 JM1248157
JM1086311
JM1248235
JM1248177
JM1248160
JM1248118
 JM1248111
JM1248122
 JM1235104
 JM1195504
 JM1153489
 JM1248076
JM1248039
 JM1248037
JM1248035
JM1248033
JM1248032
 JM1248029
JM1247992
 JM1247724
 JM1247687
 JM1247882
 JM1247879
 JM1247731
 JM1247690
 JM1247723














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
