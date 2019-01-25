#!/usr/bin/perl -w

$fnhk=$ARGV[0];
$fnsac=$ARGV[1];

`hk2sac << EOF
$fnhk
$fnsac
EOF`;
