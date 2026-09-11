from babeldoc.format.pdf.document_il import Box
from babeldoc.format.pdf.document_il.midend.layout_parser import is_box_inside_container
from babeldoc.format.pdf.document_il.midend.layout_parser import (
    merge_adjacent_figure_line_boxes,
)


def test_adjacent_aligned_figure_lines_are_merged():
    container = Box(0, 0, 200, 200)
    lines = [
        Box(20, 100, 100, 105),
        Box(25, 94, 90, 99),
        Box(25, 88, 75, 93),
        Box(20, 70, 95, 75),
    ]

    result = merge_adjacent_figure_line_boxes(lines, [container])

    assert len(result) == 2
    assert any(
        (box.x, box.y, box.x2, box.y2) == (20, 88, 100, 105) for box in result
    )


def test_lines_outside_figures_remain_separate():
    lines = [Box(20, 100, 100, 105), Box(25, 94, 90, 99)]

    result = merge_adjacent_figure_line_boxes(lines, [Box(120, 0, 200, 200)])

    assert result == lines


def test_box_inside_figure_is_detected_by_coverage():
    figure = Box(0, 0, 100, 100)

    assert is_box_inside_container(Box(10, 10, 40, 20), [figure])
    assert not is_box_inside_container(Box(90, 10, 120, 20), [figure])
