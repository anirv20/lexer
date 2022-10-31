.version 49 0
.class public super t01
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

.method public static main : ([Ljava/lang/String;)V
.code stack 20 locals 1  ; ['<args>']
    ldc 10
    ldc 20
    iadd
  L_1:
    ldc 30
    ldc 40
    imul
  L_4:
    ldc 50
    idiv
  L_3:
    ldc 5
    irem
  L_2:
    isub
  L_0:
    invokestatic Method t01 print (I)I
    pop
    ldc 10
    ineg
    invokestatic Method t01 print (I)I
    pop
    ldc 1
    ifeq L_5
    ldc 0
    goto L_6
  L_5:
    ldc 1
  L_6:
    pop
    ldc 1
    ifeq L_8
    ldc 0
    ifeq L_8
    ldc 1
    goto L_7
  L_8:
    ldc 0
  L_7:
    pop
    ldc 0
    ifne L_11
    ldc 1
    ifeq L_10
  L_11:
    ldc 1
    goto L_9
  L_10:
    ldc 0
  L_9:
    pop
    return
.end code
.end method

.end class
