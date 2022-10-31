.version 49 0
.class public super t02
.super java/lang/Object

.method public <init> : ()V
    .code stack 1 locals 1
    aload_0
    invokespecial Method java/lang/Object <init> ()V
    return
.end code
.end method

.method static print : (I)I
.code stack 2 locals 1
    getstatic Field java/lang/System out Ljava/io/PrintStream;
    iload_0
    invokevirtual Method java/io/PrintStream println (I)V
    iconst_0
    ireturn
.end code
.end method

.method static fact : (I)I
.code stack 20 locals 2  ; ['n', 'value']
    ldc 1
    istore 1
  L_8:
    iload 0
    ldc 1
    if_icmpgt L_11
    ldc 0
    goto L_10
  L_11:
    ldc 1
  L_10:
    ifeq L_9
  L_12:
    istore 1
  L_13:
    istore 0
    goto L_8
  L_9:
    iload 1
    ireturn
.end code
.end method

.method static fact_r : (I)I
.code stack 20 locals 2  ; ['n']
    iload 0
    ldc 1
    if_icmpgt L_17
    ldc 0
    goto L_16
  L_17:
    ldc 1
  L_16:
    ifeq L_14
  L_18:
    ireturn
    goto L_15
  L_14:
  L_15:
    ldc 1
    ireturn
.end code
.end method

.method public static main : ([Ljava/lang/String;)V
.code stack 20 locals 1  ; ['<args>']
    ldc 5
    invokestatic Method t02 fact (I)I
    invokestatic Method t02 print (I)I
    pop
    ldc 5
    invokestatic Method t02 fact_r (I)I
    invokestatic Method t02 print (I)I
    pop
    return
.end code
.end method

.end class
