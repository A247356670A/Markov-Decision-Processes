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
              SMTransition('4', 'a3', [ ['0', .5, 0], ['5', .5, 2]]),
              SMTransition('6', 'a1', [ ['5', 1, 3]]),
              SMTransition('5', 'a1', [ ['6', 1, 0]]),
            ], '0'
          )

        from algos import value_iteration
        pol,vivalue = value_iteration(mdp=smmdp, gamma=.9, epsilon=.01)

        from nondet import NDPolicy, compute_policy_value, compute_non_augmentable_policy

        ndpol = compute_non_augmentable_policy(mdp=smmdp, gamma=.9, epsilon=.01, subopt_epsilon=.03, max_iteration=1000)
        nvvalue = compute_policy_value(mdp=smmdp, ndpol=ndpol, gamma=.9, epsilon=.01, max_iteration=1000)

        # Verifies the ratio of the value
        for state in smmdp.states():
            diff_ratio = (vivalue.value(state) - nvvalue.value(state)) / vivalue.value(state)
            self.assertLessEqual(diff_ratio, .03)

        # Asserts that at least one state offers a choice
        # NOTE: We do not verify here that the policy is non augmentable.
        has_a_choice = False
        for state in smmdp.states():
            # print(ndpol.actions(state))
            if len(ndpol.actions(state)) > 1:
                has_a_choice = True
        self.assert_(has_a_choice)

def main():
    unittest.main()

if __name__ == "__main__":
    main()
  

# eof