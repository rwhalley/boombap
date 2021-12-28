from threading import Thread, Lock
from time import sleep

counter = 0

# Our function
def increment(num, lock):
    global counter

    #lock.acquire()

    local_counter = counter
    local_counter += num
    sleep(0.1) # creates the

    counter = local_counter
    print (f"counter={counter}")

    #lock.release()

# create lock object
lock = Lock()

# Threads
t1 = Thread(target=increment,args=(10,lock))
t2 = Thread(target=increment,args=(20,lock))

# Start Threads
t1.start()
t2.start()

# Wait for threads to complete
t1.join()
t2.join()

print(f"The final count is: {counter}")

#
# from threading import Thread
# from time import sleep
#
#
# counter = 0

#
# def increase(by):
#     global counter
#
#     local_counter = counter
#     local_counter += by
#
#     sleep(0.1)
#
#     counter = local_counter
#     print(f'counter={counter}')
#
#
# # create threads
# t1 = Thread(target=increase, args=(8,))
# t2 = Thread(target=increase, args=(20,))
#
# # start the threads
# t1.start()
# t2.start()
#
#
# # wait for the threads to complete
# t1.join()
# t2.join()
#
#
# print(f'The final counter is {counter}')
#

