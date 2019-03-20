#THIS IS A TEST, NOT MEANT TO BE USED DIRECTLY
import ari as a

example = a.Batch(5,lambda a,b: a <= b)
for i in [5,3,8,4,2,7,4,2,4,36,5,6,7,5,3,5,6,88,9,7,5,43,2,1,34,23]:
    example.add(i)
    print example.get()
