from jmcomic import *
from jmcomic.cl import JmcomicUI

# 下方填入你要下载的本子的id，一行一个，每行的首尾可以有空白字符
jm_albums = '''
JM255486
JM1127841
JM1120053
JM1101877
JM104311
JM104310
JM1088416
JM1114788
JM1027647
JM1088862
JM531306
JM416860
JM448053
JM384712
JM384710
JM297823
JM1067038
JM1060336
JM537109
JM555232
JM1052752
JM1030689
JM650898
JM639960
JM1069284
JM547740
JM212164
JM186940
JM139723
JM106042
JM92861
JM15720
JM15721
JM78212
JM77299
JM645513
JM639761
JM349464
JM310181
JM547857
JM135787
JM113685
JM113555
JM107210
JM95546
JM75614
JM72457
JM66414
JM64149
JM62881
JM61094
JM60994
JM47545
JM45953
JM45950
JM45223
JM37583
JM36815
JM36811
JM36809
JM36808
JM35665
JM36155
JM26988
JM28890
JM26917
JM6785
JM639538
JM603974
JM601981
JM599019
JM564308
JM1074922
JM1061018
JM1035106
JM1015376
JM598780
JM591661
JM583002
JM570302
JM565623
JM556696
JM554882
JM548599
JM514475
JM514474
JM513537
JM482012
JM482011
JM476098
JM461383
JM456216
JM456214
JM443837
JM443836
JM443834
JM440208
JM440066
JM440065
JM439850
JM439386
JM439385
JM432072
JM430574
JM427317
JM404484
JM399465
JM399460
JM399457
JM399455
JM399438
JM353965
JM570955
JM1016715
JM524985
JM1069053
JM1038276
JM581588
JM577460
JM542173
JM508136
JM506517
JM498606
JM498426
JM484400
JM467256
JM466120
JM465724
JM459247
JM457186
JM447305
JM440099
JM376014
JM330540
JM318166
JM291363
JM289956
JM314464
JM485637
JM260822
JM1111595
JM1111925
JM1111916
JM1111915
JM1110921
JM1110743
JM1110609
JM1107773
JM1107540
JM1107475
JM1107456
JM1107081
JM1104914
JM1104592
JM1104589
JM1104454
JM1104105
JM1093857
JM1089519
JM1077807
JM1078273
JM1054627
JM1015680
JM627021
JM627960
JM536738
JM510455
JM414384
JM413147
JM354551
JM303291
JM243543
JM227048
JM99184
JM99186
JM92970
JM82674
JM64589
JM646452
JM615107
JM613922
JM608658
JM593445
JM593444
JM589034
JM570600
JM559682
JM516253
JM514384
JM502581
JM486199
JM476099
JM114267





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
