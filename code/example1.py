'''
  An example of a state machine
'''

from statemachine import SMTransition, SMMDP

def example_1() -> SMMDP:
    return SMMDP(
        [
            SMTransition('0', 'hunt',   [ ['0',.3, 3], ['1',.7, 3] ]),
            SMTransition('0', 'nohunt', [ ['0',1., 3] ]),
            SMTransition('1', 'hunt',   [ ['0',.1,12], ['1',.2,12], ['2',.7,12] ]),
            SMTransition('1', 'nohunt', [ ['0',1.,12] ]),
            SMTransition('2', 'hunt',   [ ['1',.1,11], ['2',.2,11], ['3',.7,11] ]),
            SMTransition('2', 'nohunt', [ ['1',1.,11] ]),
            SMTransition('3', 'hunt',   [ ['2',.1,10], ['3',.9,10] ]),
            SMTransition('3', 'nohunt', [ ['2',1.,10] ]),
        ]
        ,
        '1'
    )

# eof