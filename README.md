# PsychoPyParadigms

Experimental paradigms run with PsychoPy that I’ve accumulated over the past year, including EyeLink and SMI eye tracker interfaces. 

SampleExperiment represents my current estimate of best practices in logging and timing.

GeneralTools and EyeTrackerTools should be added to PsychoPy's path in Preferences --> General --> paths.

The BasicExperiments folder contains several earlier paradigms that I played with before settling on the reading paradigm. They are not as polished, but could serve as a starting point for those wishing to implement things like them. They are:

* AudioInterspersedQuestions: play sound file and periodically stop to ask questions.
* AudtitorySartTask: Implement an audio version of the SART (sustained attention response task) described in Seli 2011 (doi:10.1037/a0025111)
* BopItTask: Audio-behavior association task based on the game BopIt.
* FlankerTask: Implement the Erikson Flanker Task described in Eichele 2008 (doi: 10.1073/pnas.0708965105)
* FourLetterTask: Implement a visuospatial working memory task described in Mason et al., Science 2007 (doi: 10.1126/science.1131295)
* LearnNonsenseWords: Play pairs of nonsense words, then display one and the subject must recall the other (multiple-choice questions)
* LocalGlobalAttention: Implements the local-global attention task as described in Weissman, Nature Neurosci. 2006 (doi: 10.1038/nn1727)
* NumericalSartTask: Implement the modified SART (sustained attention response task) described in Morrison 2014 (doi: 10.3389/fnhum.2013.00897)
* ReadingTask: Display multi-page text with interspersed thought probes (was your mind wandering?). Display comprehension questions at the end. See RunReadingComp for an alternative version.
* RhythmicTappingTask: Ask the subject to tap along with a beat, then maintain the beat after it stops playing.
* SequenceLearningTask: Implement a sequence learning task described in Mason et al., Science 2007 (doi: 10.1126/science.1131295)
* SimonTask: Audio-Visual sequence learning task based on the game Simon.
* GetPerceptualThreshold/ThresholdToneDetection(_2AFC): use staircasing to find a subject’s audio volume threshold, then periodically play tones near that threshold. _2AFC indicates a 2-alternative forced choice version of this task.
* VidLecTask: play video file with interspersed thought probes (was your mind wandering?). Display comprehesion questions at the end. See MovieTest for a simpler version of this.
