import unittest
import pygame
from game import shuffle_icons, generate_icon_positions, handle_click, check_match, use_hint, undo, handle_game_over

class TestGame(unittest.TestCase):
    def setUp(self):
        self.game_over = False  # 初始化 game_over
        self.hint_index = None  # 初始化 hint_index
        pygame.init()
        self.selected_icons = shuffle_icons()
        self.icon_positions = generate_icon_positions()
        self.clicks = []
        self.matched_icons = []
        self.undo_last_match = []

    def test_shuffle_icons(self):
        icons = shuffle_icons()
        self.assertEqual(len(icons), len(self.selected_icons), "图标数量应当正确")
        self.assertNotEqual(icons, self.selected_icons, "图标应当被打乱")

    def test_generate_icon_positions(self):
        positions = generate_icon_positions()
        self.assertEqual(len(positions), len(self.icon_positions), "图标位置数量应当正确")
        # 测试位置是否在屏幕内
        for pos in positions:
            self.assertTrue(0 <= pos[0] <= 800, "X坐标应在屏幕范围内")
            self.assertTrue(0 <= pos[1] <= 600, "Y坐标应在屏幕范围内")

    def test_handle_click(self):
        # 模拟点击第一个图标
        pos = self.icon_positions[0]
        handle_click(pos)
        self.assertIn(0, self.clicks, "第一个图标应当被选中")

    def test_check_match(self):
        # 模拟点击两个图标并检查匹配
        self.clicks = [0, 1]
        check_match()
        if self.selected_icons[0] == self.selected_icons[1]:
            self.assertIn(0, self.matched_icons, "应当匹配第一个图标")
            self.assertIn(1, self.matched_icons, "应当匹配第二个图标")
        else:
            self.assertEqual(len(self.matched_icons), 0, "不匹配时应当没有匹配")

    def test_use_hint(self):
        # 测试提示功能
        use_hint()
        self.assertIsNotNone(self.hint_index, "提示图标应当存在")

    def test_undo(self):
        # 模拟匹配成功并测试撤销
        self.matched_icons = [0, 1]
        self.undo_last_match = [0, 1]
        undo()
        self.assertNotIn(0, self.matched_icons, "撤销后第一个图标应当未匹配")
        self.assertNotIn(1, self.matched_icons, "撤销后第二个图标应当未匹配")

    def test_handle_game_over(self):
        # 模拟游戏结束
        self.matched_icons = list(range(len(self.selected_icons)))
        handle_game_over()
        self.assertTrue(self.game_over, "游戏应当结束")
        self.assertEqual(self.game_result, "恭喜，你赢了！", "应当赢得比赛")

if __name__ == '__main__':
    unittest.main()