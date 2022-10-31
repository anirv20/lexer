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
  L_0:
    invokestatic Method t01 print (I)I
    pop
    ldc 10
    ineg
    invokestatic Method t01 print (I)I
    pop
    ldc 1
    ifeq L_1
    ldc 0
    goto L_2
  L_1:
    ldc 1
  L_2:
    pop
    ldc 1
    ifeq L_4
    ldc 0
    ifeq L_4
    ldc 1
    goto L_3
  L_4:
    ldc 0
  L_3:
    pop
    ldc 0
    ifne L_7
    ldc 1
    ifeq L_6
  L_7:
    ldc 1
    goto L_5
  L_6:
    ldc 0
  L_5:
    pop
    return
.end code
.end method

.end class
