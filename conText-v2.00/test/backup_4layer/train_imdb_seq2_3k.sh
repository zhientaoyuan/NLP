
  gpu=0  # <= change this to, e.g., "gpu=0" to use a specific GPU. 

  prep_exe=../bin/prepText
  cnn_exe=../bin/conText

  #---  Step 1. Generate vocabulary
  echo Generaing vocabulary from training data ... 

  max_numk=10
  v=v${max_numk}k
  vocab_fn=data/imdb_trn-${v}.vocab
  options="LowerCase UTF8"
  
  $prep_exe gen_vocab input_fn=data/imdb-train.txt.tok vocab_fn=$vocab_fn max_vocab_size=${max_numk}000 \
                            $options WriteCount

  #---  Step 2. Generate region files (data/*.xsmatvar) and target files (data/*.y) for training and testing CNN.  
  #     We generate region vectors of the convolution layer and write them to a file, instead of making them 
  #     on the fly during training/testing. 
  echo 
  echo Generating region files with region size 2 and 3, 4 ... 

  # added by Chang, here we use another 4 region to generate a new convolutional layer  
  for pch_sz in 2 3 4; do
    for set in train test; do 
      rnm=data/imdb_${set}-${v}-p${pch_sz}
      $prep_exe gen_regions \
        region_fn_stem=$rnm input_fn=data/imdb-${set} vocab_fn=$vocab_fn \
        $options text_fn_ext=.txt.tok label_fn_ext=.cat \
        label_dic_fn=data/imdb_cat.dic \
        patch_size=$pch_sz patch_stride=1 padding=$((pch_sz-1))
    done
  done


  #---  Step 3. Training and test using GPU
  log_fn=log_output/imdb-seq2-3k.log
  perf_fn=perf/imdb-seq2-3k-perf.csv
  echo 
  echo Training CNN and testing ... 
  echo This takes a while.  See $log_fn and $perf_fn for progress and see param/seq2.param for the rest of the parameters. 
  nodes=3000 # number of neurons (weight vectors) in the convolution layers 
  $cnn_exe $gpu cnn \
         nodes=$nodes resnorm_width=$nodes \
         data_dir=data trnname=imdb_train-${v}- tstname=imdb_test-${v}- \
         data_ext0=p2 data_ext1=p3 data_ext2=p4 \
         reg_L2=0 top_reg_L2=1e-4 step_size=0.25 top_dropout=0.5 \
         LessVerbose test_interval=25 evaluation_fn=$perf_fn \
         @param/seq2.param > ${log_fn}

