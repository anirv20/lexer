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
  L_12:
    iload 0
    ldc 1
    if_icmpgt L_15
    ldc 0
    goto L_14
  L_15:
    ldc 1
  L_14:
    ifeq L_13
    iload 1
    iload 0
    imul
  L_16:
    istore 1
    iload 0
    ldc 1
    isub
  L_17:
    istore 0
    goto L_12
  L_13:
    iload 1
    ireturn
.end code
.end method

.method static fact_r : (I)I
.code stack 20 locals 2  ; ['n']
    iload 0
    ldc 1
    if_icmpgt L_21
    ldc 0
    goto L_20
  L_21:
    ldc 1
  L_20:
    ifeq L_18
    iload 0
    iload 0
    ldc 1
    isub
  L_23:
    invokestatic Method t02 fact_r (I)I
    imul
  L_22:
    ireturn
    goto L_19
  L_18:
  L_19:
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
