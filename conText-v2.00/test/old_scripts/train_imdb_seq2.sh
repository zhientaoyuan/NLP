  ####  Input: token file (one review per line; tokens are delimited by white space) 
  ####         label file (one label per line)
  ####  These input files were generated by prep_imdb.sh and included in the package. 
  ####  To find the order of the data points, see prep_imdb.sh and the files at lst/. 

  gpu=-1  # <= change this to, e.g., "gpu=0" to use a specific GPU. 
  mem=4   # pre-allocate 4GB device memory 
  gpumem=${gpu}:${mem}

  prep_exe=../bin/prepText
  cnn_exe=../bin/conText

  #---  Step 1. Generate vocabulary
  echo Generaing vocabulary from training data ... 

  max_num=30000
  vocab_fn=data/imdb_trn-${max_num}.vocab
  options="LowerCase UTF8"
  
  $prep_exe gen_vocab input_fn=data/imdb-train.txt.tok vocab_fn=$vocab_fn max_vocab_size=$max_num \
                            $options WriteCount

  #---  Step 2. Generate region files (data/*.xsmatvar) and target files (data/*.y) for training and testing CNN.  
  #     We generate region vectors of the convolution layer and write them to a file, instead of making them 
  #     on the fly during training/testing. 
  echo 
  echo Generating region files with region size 2 and 3 ... 
  
  for pch_sz in 2 3; do
    for set in train test; do 
      rnm=data/imdb_${set}-p${pch_sz}
      $prep_exe gen_regions \
        region_fn_stem=$rnm input_fn=data/imdb-${set} vocab_fn=$vocab_fn \
        $options text_fn_ext=.txt.tok label_fn_ext=.cat \
        label_dic_fn=data/imdb_cat.dic \
        patch_size=$pch_sz patch_stride=1 padding=$((pch_sz-1))
    done
  done


  #---  Step 3. Training and test using GPU
  log_fn=log_output/imdb-seq2.log
  perf_fn=perf/imdb-seq2-perf.csv
  echo 
  echo Training CNN and testing ... 
  echo This takes a while.  See $log_fn and $perf_fn for progress and see param/seq2.param for the rest of the parameters. 
  nodes=1000 # number of neurons (weight vectors) in the convolution layers
  $cnn_exe $gpumem cnn \
         nodes=$nodes resnorm_width=$nodes \
         data_dir=data trnname=imdb_train- tstname=imdb_test- \
         data_ext0=p2 data_ext1=p3 \
         reg_L2=0 top_reg_L2=1e-3 step_size=0.25 top_dropout=0.5 \
         LessVerbose test_interval=25 evaluation_fn=$perf_fn \
         @param/seq2.param > ${log_fn}


