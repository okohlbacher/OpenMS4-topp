cask "openms4-topp" do
  arch arm: "arm64", intel: "x64"

  version "1.0.0-ci.2,f257c6d7d7a8"
  sha256 arm:   "6fee2ced03153757e51b7c0ebe324efc5b7c7e03a4780be86573f3abac13396f",
         intel: "7ad017c823846a909abc79b36ede68c3b849b0b7b87587341865233fe5f07907"

  url "https://github.com/okohlbacher/OpenMS4-topp/releases/download/" \
      "topp-v#{version.csv.first}/OpenMS4-topp-macos-#{arch}-Homebrew-#{version.csv.second}.tar.gz"
  name "OpenMS TOPP tools"
  desc "Command-line mass-spectrometry tools built against the OpenMS Core SDK"
  homepage "https://github.com/okohlbacher/OpenMS4-topp"

  depends_on formula: "okohlbacher/openms4-core/openms4-core"
  depends_on macos: :sequoia

  payload = "OpenMS4-topp-macos-#{arch}-Homebrew-#{version.csv.second}"
  %w[
    AccurateMassSearch AssayGeneratorMetabo AssayGeneratorMetaboSirius BaselineFilter CVInspector ClusterMassTraces
    ClusterMassTracesByPrecursor ConsensusID ConsensusMapNormalizer DTAExtractor DatabaseFilter DeMeanderize
    Decharger DecoyDatabase Digestor DigestorMotif EICExtractor Epifany
    ExternalCalibration FalseDiscoveryRate FeatureFinderCentroided FeatureFinderIdentification FeatureFinderLFQ
    FeatureFinderMetabo FeatureFinderMetaboIdent FeatureFinderMultiplex FeatureLinkerLabeled FeatureLinkerUnlabeled
    FeatureLinkerUnlabeledKD FeatureLinkerUnlabeledQT
    FileConverter FileFilter FileMerger FuzzyDiff GNPSExport
    HighResPrecursorMassCorrector IDConflictResolver IDDecoyProbability IDExtractor IDFileConverter IDFilter
    IDMapper IDMerger IDPosteriorErrorProbability IDRTCalibration IDRipper IDScoreSwitcher
    IDSplitter INIUpdater InternalCalibration IonMobilityBinning IsobaricAnalyzer IsobaricWorkflow
    JSONExporter LuciphorAdapter MRMMapper MRMPairFinder MSFraggerAdapter MSGFPlusAdapter
    MSstatsConverter MaRaClusterAdapter MapAlignerIdentification MapAlignerPoseClustering MapAlignerTreeGuided
    MapNormalizer
    MapRTTransformer MapStatistics MassCalculator MassTraceExtractor MetaProSIP MetaboliteAdductDecharger
    MetaboliteSpectralMatcher MultiplexResolver MzMLSplitter MzTabExporter NoiseFilterGaussian NoiseFilterSGolay
    NovorAdapter OpenMSDatabasesInfo OpenMSInfo OpenPepXL PSMFeatureExtractor ParquetConverter
    PeakPickerHiRes PeakPickerIM PeakPickerIterative PeptideIndexer PercolatorAdapter PhosphoScoring
    ProteinInference ProteinQuantifier QCCalculator QCEmbedder QCExporter QCExtractor
    QCImporter QCMerger QCShrinker QualityControl RNADigestor RNAMassCalculator
    RNPxlXICFilter Resampler SageAdapter SeedListGenerator SemanticValidator SequenceCoverageCalculator
    SimpleSearchEngine SiriusExport SpectraFilterNLargest SpectraFilterNormalizer SpectraFilterThresholdMower
    SpectraFilterWindowMower
    SpectraMerger SpectraSTSearchAdapter StaticModification TICCalculator TextExporter UniPEFF
    XFDR XMLValidator
  ].each do |tool|
    binary "#{payload}/bin/#{tool}"
  end
  binary "#{payload}/bin/FileInfo", target: "OpenMSFileInfo"

  postflight_steps do
    run "/usr/bin/xattr",
        args:           ["-dr", "com.apple.quarantine", "."],
        chdir:          ".",
        writable_paths: ["."]
  end
end
