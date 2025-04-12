from jmcomic import *
from jmcomic.cl import JmcomicUI

# 下方填入你要下载的本子的id，一行一个，每行的首尾可以有空白字符
jm_albums = '''
JM1120109
JM1117279
JM1117278
JM1116811
JM1115865
JM1111965
JM1073996
JM1035158
JM1032483
JM1021995
JM1021469
JM639579
JM629912
JM616073
JM629910
JM614423
JM608657
JM600040
JM603136
JM603118
JM599493
JM593491
JM593473
JM589939
JM575801
JM572360
JM571561
JM570305
JM570206
JM570195
JM568346
JM568081
JM565960
JM565160
JM561424
JM556852
JM555488
JM552448
JM552446
JM547411
JM547260
JM542631
JM542629
JM542530
JM534886
JM529461
JM524516
JM523170
JM524132
JM523166
JM522014
JM520591
JM520590
JM517021
JM499249
JM481555
JM483385
JM480847
JM480583
JM476307
JM474873
JM468897
JM466138
JM468745
JM438253
JM414314
JM432880
JM403169
JM372373
JM133919
JM242341
JM242340
JM149312
JM150068
JM185523
JM287681
JM303068
JM369505
JM32862
JM32821
JM32550
JM32469
JM32200
JM28649
JM28647
JM28644
JM28137
JM28631
JM28634
JM28636
JM28086
JM27012
JM26665
JM26044
JM22010
JM23315
JM25575
JM21219
JM20988
JM19008
JM16547
JM16548
JM16550
JM16552
JM16542
JM15147
JM14268
JM321
JM3373
JM10250
JM10251
JM317
JM241801
JM240179
JM240171
JM236671
JM229052
JM230436
JM233690
JM226531
JM224503
JM222180
JM220461
JM219402
JM213628
JM209178
JM208609
JM193127
JM179910
JM180020
JM182289
JM187385
JM179902
JM179900
JM179897
JM179607
JM178275
JM177891
JM177671
JM152379
JM12834
JM151459
JM4536
JM147166
JM141492
JM146496
JM146276
JM144894
JM144085
JM144088
JM144772
JM144873
JM144083
JM144082
JM144080
JM144078
JM10786
JM4674
JM10558
JM4535
JM4531
JM141901
JM141788
JM140156
JM140151
JM139655
JM139158
JM138137
JM139369
JM139654
JM138035
JM135770
JM134983
JM133100
JM123033
JM125482
JM127278
JM130474
JM122349
JM123027
JM121580
JM120979
JM119108
JM111436
JM102787
JM1020108
JM101858
JM101859
JM101862
JM101863
JM101841
JM101797
JM101791
JM101766
JM101764
JM101581
JM101416
JM100964
JM96098
JM89430
JM89429
JM89084
JM83825
JM80796
JM78967
JM74804
JM65554
JM65458
JM63887
JM62939
JM63188
JM62330
JM61873
JM61855
JM60239
JM60200
JM60201
JM60207
JM60208
JM60198
JM60183
JM59845
JM54743
JM54727
JM50280
JM50279
JM49033
JM49034
JM49036
JM50276
JM49031
JM49029
JM49026
JM44750
JM45226
JM46794
JM48483
JM44434
JM44322
JM42653
JM39470
JM38036
JM38037
JM37483
JM36552
JM36279
JM36124
JM35895
JM34890
JM34442
JM33700
JM368776
JM359552
JM351652
JM350282
JM345572
JM342915
JM334857
JM322539
JM322863
JM317731
JM315062
JM309824
JM305578
JM304777
JM297446
JM288644
JM294220
JM287641
JM287373
JM285801
JM285506
JM281016
JM281008
JM280939
JM279468
JM146834
JM178617
JM143526
JM139091
JM142080
JM152007
JM220792
JM277920
JM277699
JM275744
JM275743
JM275619
JM274898
JM272659
JM272477
JM272278
JM268249
JM270834
JM272258
JM267459
JM264773
JM256754
JM261600
JM251858
JM249922
JM248881
JM248602

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
