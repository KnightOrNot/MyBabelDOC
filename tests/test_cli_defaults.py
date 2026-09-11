from babeldoc.main import create_parser


def test_cli_omits_watermark_by_default():
    args = create_parser().parse_args([])

    assert args.watermark_output_mode == "no_watermark"
