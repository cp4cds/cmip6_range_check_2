from multiprocessing import Process, Queue
import os, random, uuid

class Actor(object):
  ni = 0
  def __init__(self):
    pass

  def info(self,title):
    print title
    print 'module name:', __name__
    if hasattr(os, 'getppid'):  # only available on Unix
        print 'parent process:', os.getppid()
    print 'process id:', os.getpid()

  def f(self,name,q):
    self.info('function f')
    self.__class__.ni += 1
    print 'hello', name, self.__class__.ni
    q.put( (name, os.getpid() ) )

class Enact(object):
  """Class to wrap a function for use with a multiprocess queue;
      usage:   e = Execute( arglist, Enact(myfunction), myPostProcessing)
  def __init__(self,f):
    self.function = f

  def __call__(self,a,q):
    res = self.function(a)
    q.put(res)
    

class Execute(object):
  def __init__(self,args, actor, postact):
    """ args: a list of elements of type X
        actor: a function, arguments (a,q), where a is an element of args (type X), appends a result to queue q.
        postact: takes a single argument corresponding to output of actor
    
    self.args = args
    self.executing = list()
    self.execMax = 10
    self.q = Queue()
    self.actor = actor
    self.postact = postact

  def next():
    if len(self.executing) < self.execMax:
      arg = self.args.pop(0)
      p = Process(target=self.actor, args=(arg,self.q))
      p.start()
      u = str( uuid.uuid1() )
      self.executing.append((u,p))
    elif self.q.qsize() > 0:
      this = q.get()
      self.postact(this)
    
  def run(self,pauseMs=10):
    while len(self.args) > 0:
      self.next()
      sleep ....
    

if __name__ == '__main__':
    a = Actor()
    q = Queue()
    a.info('main line')
    p = Process(target=a.f, args=('bob',q))
    p.start()
    p.join()
    p2 = Process(target=a.f, args=('john',q))
    p2.start()
    p2.join()
    print '------------\n%s' % Actor.ni
    while q.qsize() > 0:
      this = q.get()
      print this
