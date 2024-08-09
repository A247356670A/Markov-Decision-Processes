import unittest


class Test(unittest.TestCase):

    def test(self):
        from dungeon import basic_map, DungeonMDP

        map = basic_map()
        mdp = DungeonMDP(map)

        import statemachine
        smmdp, statedict, actiondict = statemachine.state_machine_from_mdp(mdp)

        # from statemachine import SMMDP, SMTransition
        # smmdp = SMMDP([
        #     SMTransition('1', 'a1', [['2', 1, 3]]),
        #     SMTransition('2', 'a1', [['3', .5, 5], ['4', .5, 10]]),
        #     SMTransition('2', 'a2', [['3', 1, 2]]),
        #
        #     SMTransition('3', 'a1', [['1', .5, 5], ['6', .5, 8]]),
        #     SMTransition('3', 'a2', [['1', .9, 10], ['7', .1, 0]]),
        #     SMTransition('4', 'a1', [['5', 1, 1]]),
        #     SMTransition('4', 'a2', [['5', .9, 10], ['7', .05, 0], ['8', .05, 0]]),
        #     SMTransition('5', 'a1', [['6', 1, 1]]),
        #     SMTransition('6', 'a1', [['4', 1, 1]]),
        #     SMTransition('7', 'a1', [['8', 1, 0]]),
        #     SMTransition('8', 'a1', [['7', 1, 1]]),
        # ], '1')

        from connectedcomp import compute_connected_components
        ccgraph = compute_connected_components(smmdp)

        self.assertEqual(len(ccgraph.roots()), 1)
        self.assertEqual(ccgraph.nb_components(), 60)



def main():
    unittest.main()


if __name__ == "__main__":
    main()

# eof
