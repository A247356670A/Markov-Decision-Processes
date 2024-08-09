import unittest

class Test(unittest.TestCase):

    def test(self):
        from statemachine import SMMDP, SMTransition
        smmdp = SMMDP([
              SMTransition('0', 'a1', [ ['1', 1, 1]]),
              SMTransition('0', 'a2', [ ['1', .5, 1], ['2', .5, 0]]),
              SMTransition('1', 'a1', [ ['3', 1, 2]]),
              SMTransition('1', 'a2', [ ['3', .5, 2], ['4', .5, 1.5]]),
              SMTransition('2', 'a1', [ ['4', 1, 2]]),
              SMTransition('3', 'a1', [ ['5', 1, 1]]),
              SMTransition('4', 'a1', [ ['6', 1, 0]]),
              SMTransition('4', 'a2', [ ['5', 1, 1]]),
              SMTransition('4', 'a3', [ ['0', .5, -1], ['5', .5, 2]]),
              SMTransition('6', 'a1', [ ['5', 1, 3]]),
              SMTransition('5', 'a1', [ ['6', 1, 0]]),
            ], '0'
          )

        from algos import value_iteration
        pol,vivalue = value_iteration(mdp=smmdp, gamma=.9, epsilon=.01)

        from nondet import NDPolicy, compute_policy_value

        # create a non-deterministic policy that is actually the deterministic policy # should have the same value as the deterministic policy
        ndpol = NDPolicy()
        ndpol.add_det_policy(mdp=smmdp, pol=pol)
        nvvalue1 = compute_policy_value(smmdp, ndpol, gamma=.9, epsilon=.01, max_iteration=1000)
        for state in smmdp.states():
          self.assertAlmostEqual(vivalue.value(state), nvvalue1.value(state))

        # add action a2 to initial state # The value of state '0' should drop down to 13.6
        ndpol.add(smmdp.get_state('0'), smmdp.get_action('a2'))
        nvvalue2 = compute_policy_value(smmdp, ndpol, gamma=.9, epsilon=.01, max_iteration=1000)
        self.assertAlmostEqual(nvvalue2.value(smmdp.get_state('0')), 13.6, delta=.1)

def main():
    unittest.main()

if __name__ == "__main__":
    main()
  

# eof