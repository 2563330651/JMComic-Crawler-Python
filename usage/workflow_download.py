from jmcomic import *
from jmcomic.cl import JmcomicUI

# 下方填入你要下载的本子的id，一行一个，每行的首尾可以有空白字符
jm_albums = '''
JM1125217
JM1061026
JM1036185
JM1036216
JM1073944
JM1037288
JM1124349
JM1125242
JM393745
JM404137
JM404131
JM405302
JM601119
JM629
JM18928
JM4075
JM1863
JM3469
JM405498
JM403853
JM1124892
JM1115975
JM1120072
JM1112278
JM1113856
JM830
JM829
JM413361
JM845
JM1125310
JM1114902
JM1116828
JM231
JM90063
JM448726
JM458412
JM1125375
JM1081399
JM1125376
JM1125374
JM1125373
JM1125369
JM1125362
JM1074951
JM1065596
JM1073385
JM1114751
JM106091
JM97181
JM107952
JM107474
JM310597
JM414711
JM1114752
JM145504
JM195818
JM1114754
JM356488
JM323359
JM273336
JM302608
JM442959
JM447072
JM447068
JM405485
JM898
JM601116
JM390371
JM402868
JM152637
JM601119
JM191091
JM102658
JM179238
JM1124683
JM184505
JM1124686
JM232647
JM148993
JM326164
JM114842
JM255300
JM255485
JM301222
JM302575
JM264883
JM214490
JM208609
JM177680
JM206046
JM144955
JM302820
JM151144
JM178277
JM221309
JM390131
JM291605
JM179584
JM180599
JM326197
JM390132
JM196438
JM302366
JM199646
JM181371
JM566986
JM185023
JM296782
JM151272
JM390128
JM302471
JM179253
JM390127
JM272886
JM141492
JM601120
JM281397
JM301258
JM293534
JM302821
JM302276
JM181716
JM302122
JM112952
JM404005
JM236959
JM149294
JM180491
JM303074
JM248002
JM205819
JM249791
JM218293
JM208093
JM184628
JM302550
JM85250
JM390130
JM254931
JM302490
JM302996
JM148838
JM85462
JM326176
JM113620
JM208122
JM148997
JM277707
JM241077
JM264573
JM256607
JM205460
JM302759
JM271913
JM203616
JM301410
JM292954
JM255372
JM298580
JM303070
JM302474
JM222187
JM206567
JM292628
JM129910
JM269538
JM282293
JM195520
JM127149
JM279102
JM283429
JM190797
JM195491
JM291396
JM212775
JM302556
JM263003
JM278471
JM264793
JM301958
JM179899
JM279092
JM302466
JM310597
JM243109
JM302514
JM287234
JM218584
JM302618
JM179377
JM179902
JM246410
JM143092
JM235357
JM73951
JM253179
JM302472
JM305105
JM255251
JM302513
JM296135
JM247433
JM249263
JM302829
JM427111
JM313472
JM302755
JM273085
JM137424
JM302784
JM181495
JM140151
JM233715
JM302555
JM248881
JM185523
JM303892
JM221448
JM74549
JM303714
JM226836
JM601117
JM209706
JM259021
JM302397
JM220691
JM148717
JM147715
JM302781
JM293464
JM224358
JM193773
JM300457
JM135770
JM234532
JM297446
JM258427
JM205827
JM178548
JM302808
JM303069
JM146608
JM301917
JM97181
JM256209
JM302457
JM279111
JM180454
JM214842
JM22263
JM66
JM215435
JM205606
JM147166
JM147
JM302559
JM289999
JM144431
JM186781
JM247341
JM221701
JM121674
JM216659
JM118391
JM300995
JM221686
JM235551
JM271258
JM196248
JM301939
JM231157



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
