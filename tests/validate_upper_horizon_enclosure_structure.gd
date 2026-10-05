extends SceneTree
# Actual imported geometry, fixed-floor preservation and rooted architectural
# contacts only. This does not certify loads, pressure, final art or species fit.
const CONTRACT := "res://data/architecture/UPPER_HORIZON_ENCLOSURE_RUNTIME.json"
const AUDIT := "res://docs/UPPER_HORIZON_ENCLOSURE_SOURCE_CONTACTS.json"
const ROUNDTRIP := "res://docs/UPPER_HORIZON_ENCLOSURE_SOURCE_ROUNDTRIP.json"
const PARTS := "res://data/architecture/UPPER_HORIZON_ENCLOSURE_GEOMETRY_PARTS.json"
const EPS := 0.001
const MAX_RESULTS := 256
const FLOOR_Y := 106.5
const SLAB_BOTTOM := 106.26
var asset_path := "res://assets/models/AST-CMD-006.glb"
var expected_batches := 448
var enclosure: Node3D
var enclosure_exclusions: Array[RID] = []
var enclosure_triangles := 0
var solid_witnesses := 0
const PRESERVED_HASHES_JSON := """{"assets/models/AST-CIR-005_upper_link.glb":"6a246dbf565a1874f60cb3d0f9a549b9228b5a0875ba73dc734121f6f607d60d","data/architecture/AFT_CROWN_LINK.json":"620d26f88b914b778c41006592f7a7b42a9d480b341101ea3f40b908f781f342","data/programme_ledger.json":"7ad90e3322ef4ce666262d0d27e191f85bf7480fc6e5f2c312f5574c69ca2366","data/reference/historical_guest_census.json":"9436f006b2e71f6ee5bda71cd8dc09d1c52f44844027fa7082e3b286a7215038","data/reference/D03_crew_envelopes.json":"6473d78e789860594c6a955268d7ecc7f0ff44b130cc3ccc833b857e4513ec81","data/design_contract.json":"8790e9997fd39c6ddd8a494f665b2a438a7160ec31f343bd858ce5c036fa569a"}"""
const FLOOR_IDS := ["D18_aft_crown_platform_foyer_port","D18_aft_crown_platform_foyer_starboard","D18_aft_crown_platform_upper_horizon_port","D18_aft_crown_platform_upper_horizon_starboard"]
const PIER_CENTRES := [Vector2(-9.5,119),Vector2(9.5,119),Vector2(-9.5,148),Vector2(9.5,148),Vector2(-35.5,174),Vector2(35.5,174)]
const OLD_RECORD_HASHES_JSON := """{"D01_fore_route":"713d3a3e49fd0ec84772061f4088271768156c867e9dd6656257df3cb4771d62","D01_aft_route":"b02c393015a5b80f61cbaaae394cec44dee6a23bf322b605e3dc9b3d161bf19b","D01_fore_apron":"90231167f2298416c36ecfb1a0d9e9eb2882ff90a53b372ba63ddd6bc1bdfe92","D01_aft_apron":"a3ad95cb23bd3a3a4e0e9690b0a21b7bf75b52c3ec555418297715044315dfaa","D01_service_side":"3cf8defce1569ee1f26b8a62324af5ad909462f656f238b5acecfada7d25cd9d","D02_fore_route":"799ef47189f82a1aeec86222593304a38e20dadcb086bbc492460876a230b1a0","D02_aft_route":"641c1bc9b5bd2bb114fbdaf326548d275a4c59fcde477b0f816a8ebd4954f634","D02_fore_apron":"32ccb0d8b1ad07915f4d733565568c16e42aaf8e84d3a033d1537364d680b36a","D02_aft_apron":"a0b284811fe6085809e3de69733874dd43d7724f87d94dea38dfb7b8e14357c2","D02_atrium_circulation":"5b3d5b711f12508820cf2ac91b7e683cf77bb5805eb5b7388e5a045fad4cc725","D03_fore_route":"9b0c7822f4c6553a4df47b8820b1d03e1fc9303fcce73fdf18d4520aaaa812ff","D03_aft_route":"5ce4ba1c1daafb632fec07c3350018e7205de039a6223e3ed652575cdc8be9a2","D03_fore_apron":"f7d7fb348a8fc3dc5c0d9f8b771e7de33955ea298f081be79158ebdd1c4e7618","D03_aft_apron":"51a557abb02ebe2f068a7befecc9f071f95133d9796cc17bcd5f1f5e07d1d617","D03_atrium_circulation":"0cc11560a713dbef2407c1eb83e182b80db167e18c957573be8d3541017a9b27","D04_fore_route":"fc775c6f784b879af5c9726c8a73dd72255c2f8e8a65c351127529b9ff6fc093","D04_aft_route":"d21e06d8eced620fb2b07a360990d649c33a8aac3ab63fff17d6382143cca98d","D04_fore_apron":"7a9b45d1bd9e6e0c7bb1489cb59ea0072f3f7df0acaeb3517237c5133258c090","D04_aft_apron":"b10df7b198c5f49c5a1840677c2e53a7365274570e176133de1806c27d6c46f5","D04_atrium_circulation":"e521618efaeb2ceaa8356d962d9c0f799eb3d652ee7353c9cef8d448f0db4b13","D05_fore_route":"c08bbc3917731d079bfb5a9e1af9b8d1d089c2cc8afff317561445a50508893d","D05_aft_route":"fd3dc4ba9aa10c975133e94ae9dc8cb43a9457e5296a67e88ffb6b5ac6b08694","D05_fore_apron":"1ed0b6e4bc8eb8c2b8b742b41d25bfd2bb1c7d33309121dabdcf047a92eb0bbf","D05_aft_apron":"41b68fcd7fb78fcda4eca55d676062fdec84413b2fac6486de24997d90b65863","D05_atrium_circulation":"d827b9af45d68cf7583062b811b3cbe74d1eb460b6f10c69112df72afe076395","D06_fore_route":"b1b00e587ef5d61791b63f1163ceea67c018c0ff9af404eee3a1fd1212afbea7","D06_aft_route":"a83b8689f082efcd8b8113875c7cd542619dcc76d63dd476459a574da2762a10","D06_fore_apron":"6e78e3b9c5a5e67ecc520372503a608a8dd82a477708938d7290b1cc8248f8f4","D06_aft_apron":"fbfe10d4673d24895cd232a70e215e671cbfa574f72571dd71b76d24338cfbea","D06_atrium_circulation":"9f58ae06e11be9f2a2daa7d93e69bfc7e4b7cc91cc05f7fcc53f0e43f4f8e66c","D07_fore_route":"8da839238769ecd7fede1d7ee0bfa403f5977315900641798eb2aabacbf877fe","D07_aft_route":"8d8a2a33399cd27d9ca4c4738832a598bbeeff9e6d82dc4820b39b270efa92fb","D07_fore_apron":"7607da8e671c17ca611ed4c46bd9de868feae36460e5e9eaa4c34efbc4826b32","D07_aft_apron":"48711b98e2f5764a467a7477aa99ea20171dd9db02d91be97b7c199b18871771","D07_atrium_circulation":"5b12b398d3b93399f3b4dcfd7362e92e002bbb008b36678e4fd5e1a0aa67e6af","D08_fore_route":"5f26fa84334338e63b3922658cfd11b4ffc71b3a6cb2bbe48bac755326427903","D08_aft_route":"f72888b067e776189108e5a34d0e3e0933083156e6cea424426ed1bb3294a1ee","D08_fore_apron":"04046354287b63ef04abff03a57478dad9bca65e65e03e4bd2c9e41ede8e4b8d","D08_aft_apron":"ef30a74aedb5f27b999b3a47821e996113cad67b4c86701e6706db4cd41ac84a","D08_atrium_circulation":"156b12fad52596dc067a1be85294bb5f45514462675e2e0e495e7ae5aab63ef1","D09_fore_route":"d9fb18c6426b547f33cd82e5b02edbefcec5534a6fd56774535336060926d51e","D09_aft_route":"943c029cbc42ce2574126db8c1e989149597c380a0d0fb14d77c48fad836bff9","D09_fore_apron":"f03e3fb802110a12eff9d546ff4b18712a96ff5adb315236d0ceeecb6f9be3d7","D09_aft_apron":"54164b336e47afbd1f1dbcc07211eccf2a427e460f92b5cf78dc392b07b809c9","D09_atrium_circulation":"242af55549c0b2e92777781ee45830417f205eb23d63578c6d45a677703d856f","D10_fore_route":"6d313176d5431e58d98399ea043b148b3b156fcef894842a18fcffccc1dbdbc7","D10_aft_route":"6c59a8671cdb2ea426c755f348e550726756a53a8b23ac2976ce1b283daed9c6","D10_fore_apron":"a3eb870ac4dce802a51c005d9690569cb0f4c5c6e7cfd6abbe876bb968908381","D10_aft_apron":"685d890632c411253dd56efa02d2cb7fc77ac1ffd9be079dd69fd31a169a3dac","D10_atrium_circulation":"2f291fdc737f7b8ecd78a816bc020442025e889643a0227abf2afc6ecf559f2e","D11_fore_route":"552ddd1998e3a4b1076342df34569e0d63549edd35ee8befccabe9b048b084d6","D11_aft_route":"393eddc0c818f06d3339d7e5c9cc270e6d9ceb71a1ecb517d90ce8e70cdd4d0b","D11_fore_apron":"615341b1b265dd813b4ca2f1cf279e362776722f8b544f7247e5e613309592a0","D11_aft_apron":"616a1fa5eddd68f6cd06aa57a4e79441470523693eb7ff29348a6ad3ff42c026","D11_atrium_circulation":"5f5ff389fab7e34cc2e4bb1c602adc2bb99bf44254bad00c6f7c7e86dc5c867e","D12_fore_route":"baa3063a2579a45b66a25f88d86d3733681daca1c0e6fc7f0b08b5598692a53a","D12_aft_route":"9f4688553fb668b20e76d9dcf3f3ab35bf4db8c6519ffc5c173a29073c03b959","D12_fore_apron":"465c8130243fc76b560765ace9b99fe374bfc1ba6f4de1ee599da943093cfbe6","D12_aft_apron":"3ad1d6659a76432e637f1de26a6f204406d8f404547f5272fc14c7b035eb5616","D12_atrium_circulation":"34ef89d1ee889b60e6a7fde52fbcbe9191757eb05d40fe9d117f3311ca872954","D13_fore_route":"3e4d9df4b94ffbcb8679e0e2fcc5006693414e9d365def8b363aa3ced2d60634","D13_aft_route":"4ce9dbcdcbc7f61961a5e40dd808dc4d6e2f3c773a70fc09975bf281510a8571","D13_fore_apron":"8f65042467bd034a6ba5950988a751698fa7d678b2f32eaca0b9c0de4882e096","D13_aft_apron":"cff1d988b5b7fa636a6cb42c2590bcab829eb350a681dba8fa7a1e9d09a1559f","D13_atrium_circulation":"ce7110e911ffd61734115cb318ae35cd7502d2e10402c8e43c2936fdf3037ded","D14_fore_route":"92249d0a4acc887db826797d58c01e5b4efd60497b4bd032007fc14829ba00c0","D14_aft_route":"1e9013b2074ea818438ed137d730555dc594b0d5de26bd30cee99b0172f59610","D14_fore_apron":"7eb20868fad68f9fc169a0de617ad195c388f67319a30071f5afc082264daae3","D14_aft_apron":"13a77aa5b8d25ee21f7346b01ecba98e7fde0d74523021c54e0ca19711d91eb1","D14_atrium_circulation":"b95da7eae21b548ff8b359ae12d4253fd0ca703a3ab745bd2e1a6c7b261c8f51","D15_fore_route":"fe08b8005e2f4b226bee2dd3f17c18895b45921717ea27cc06fbdfd47c77a75f","D15_aft_route":"51bcf3dfe84a5beb1c37ebf98f13355f2dc2952ae6244e953f6a29c30e7b3e75","D15_fore_apron":"ef4386c0557b342bc1cdf36a60c37f44ce14cd9c0f4bfbe5e3903ec2dab8ae58","D15_aft_apron":"6faa6ecc2331c81a138af306064e262b6203eb322f323ca77828c9a4de248f2f","D15_atrium_circulation":"faa9eac3b0df45259d86a7f05daeb42a6320458d07292dff4e02de9295e71a92","D16_fore_route":"ceed3829bbff1652121ead008ed3ecf539121bf12827a1edc861450d54a9b988","D16_aft_route":"a69ad089adf70641624604c7fe5c1c472cfc73cded5067764270b6acdbe206dc","D16_fore_apron":"323a2d2a9323f49e852ca5a32262cd17a70f6cc6bc9ac4f622a314de5084dc99","D16_aft_apron":"35cc6017266de3a6e39d1b432d03f6680b222090f9e45f0c967608768ecb09d7","D16_atrium_circulation":"1a3bec15018c155a29f90b9f9334c08c73fd279fbff29c725d047eb918fa0dff","D17_fore_route":"02df4e4aa6b583e0093079fdd8a6f528a600d64fe27a5b13e099e2e2fd80a942","D17_aft_route":"1450c676b2f6cc3db8a180fa7d0b4f1121d338a462eb00251484abbb668c1ccf","D17_fore_apron":"8c2aafaa2d1863245796e001f988f2e4d6e49ad5968c5df5efc03bd7a974f7aa","D17_aft_apron":"f3e0f332837255b0d103e8d04d878b9a0a1670e0e4cac5d82184b81af5233b84","D17_atrium_circulation":"3ffe78c3fa09d6f7cbf422e9a6e6bf95a7f68468e7f1478c3511a1b964fa3e66","D18_fore_route":"bebfcc2442e44ca75c5a21a930ea1b1d562a965069719f7fd4819d85c97034dc","D18_aft_route":"3d2a621e62123e99b17e09f56be3926dde29446d77b3a76f2a15c706c836842d","D18_fore_apron":"360cb4ac5bd2e8d48cc9e35cd13172f316e896984df185c765721db617d8b309","D18_aft_apron":"3a7137873e7f9a1cb022248f88c4fa136b78b093353dbed76696a53a7f3f59e9","D09_salon5_initial_terrace":"9f1ae9465c96f9ccb7027c2dd5d93b41b6524e3b8c1f3ad06ce4a85469573a6b","D08_gentle_waters_floor":"7481b00e7e3f93a3cef7d9ed1dfb5d6a570ecfb7a3f16991d4f63c4218a24133","D08_aquatic_district_arrival":"dfe708bd7da932cc087e930edb14396a3569a68d94e115c47c4248598d993893","D09_living_gifts_floor":"cd70da58c7396e67f00ce95b85e948ec8a1894f74f7408b1023a3ebcc3474ae0","D09_aquatic_district_arrival":"25c55d353a1e419d8f0b3fc4c2f0fcda6c1a9155fb86d3d925863a7c5658e443","D10_vesper_floor":"43f0eb47163b10de6df6a3534519e88dffbe1b3617dab14389a8f387b79d9253","D10_aquatic_district_arrival":"9a2f14228046337d96cf80cfb7303ce6d2bcc483a835de003496c4593cfd901c","D08_gentle_waters_basin":"b538e115016362806c30405ebeffe3318dccc718ec6601f1432b2f33cf6b9a7a","D01_port_service_spine":"41e7076dbbea9e1f86caea2b2e2096d564826d7e8ebbd6b11389b62286f5ea35","D01_synthesis_service_bay":"53c64da42fdef3843f9edd78c8bd9d3000314162ab3d58c40b9927cce4d08d84","D02_authored_atrium_terrace":"4df9066266955c6c1071a0aa361f7735ddce244b51498ebf0d84761e5d199641","D03_authored_atrium_terrace":"3b823a273503dd9baeda1ad37dd5908445bbb764134f79a26fd41c481f5da749","D04_authored_atrium_terrace":"ec740a73c801ecba99d22f4a3010f70270817dc9f67d82755e22302bfe84d27a","D05_authored_atrium_terrace":"fc48bd4d58541bc367d01b1e14fbf85d85b262a707ea6561dff67a27e05b438d","D06_authored_atrium_terrace":"8450c2f3097e01995e551f45bb7527a294a11dbf212af40b85e2caec97cb2a50","D07_authored_atrium_terrace":"e0bd2dbdc886bab1c789a8c7f49b54b4025f85264a461f0cf3d4654f9e35ec31","D08_authored_atrium_terrace":"f901fd0b1808839b7e064fc428348ab83ea75f4fec87b88b36a25e91db4eaa8b","D09_authored_atrium_terrace":"0a30cd54b57a1760d58dc821bdcb9ed560a685b5422a0b8b1a341e85dc57c246","D10_authored_atrium_terrace":"acaeaae80792e4f761eb3830d609af00f11aec43d352eb93c5d1c4f22e26df92","D11_authored_atrium_terrace":"4360446ee48d178d1ec64ec412c0207a6bc78e29f6fc393ecd691c533a66c168","D12_authored_atrium_terrace":"0c344c2a1e4555233c62e45ae77735176419a023b0e7c5564d7f68e492d7e7e8","D13_authored_atrium_terrace":"c62c5e714283e4d073125a84be014a32d6e86139d5e3beefe6d8912f6b9cd0d7","D14_authored_atrium_terrace":"e9cefc39daa14dafd0d745375d3d08ea19a25c9300c4ba5c23d2db79befa0a1c","D15_authored_atrium_terrace":"a83d5d9b7d9620f8ad6f928c9830a6b541fe6bc72e69345c9acde4ec2f6aad55","D16_authored_atrium_terrace":"879b078696ca20ae88edd5027fa2c0f9d6f123a92fc5d6010df4e3ad64f949dc","D17_authored_atrium_terrace":"0cebc0620bdcd83a1126e443af1711df2ec12a3da28a58e02199550c5748c402","D01_central_service_axis":"7c3df3729d9f7e5e8502c624e34af3ae551d69dc0ed62dfa9422694975f9637d","D18_atrium_structural_cap":"136f8b3f54aa923bf11ea1a81d1de209c407042596a952491194859a100ed84a","D02_garden_dry_court":"e1516f8d9f095ab8e9978cfb6fcc4be49e8028dd51cf1c167283c63cb1f9f00d","D02_garden_pool_1":"b94fd39f7304dfd267bf3bc175e5efa3163e9ffabd2a031a953dd1bed5eebe0d","D02_garden_pool_2":"ee9764a0e916ff3eda59bf5bd0736d46d7226df755d4f54198cd0b2c71cbbd87","D02_garden_pool_3":"fc277156905e449e3db4769d30e19b8a2d1c620a02300ae4d7c5896fa5880a97","D02_garden_pool_4":"874e9a1ee4064fd809e391327e55299736f26b648026a9fe3acbe982b7bad651","D13_residential_street_connection":"4ea19c8b6dad6b1a61631340a1cff1d713d3692f1ac2d7884c58d6326725aba2","D13_residential_street_pilot":"a8a543dd79ebf3c6649456434c12685163181bf58a94274f3a8f451e564ef5bf","D13_window_terrace":"208735bce819ed945a2602a6c74d74a6f3651aa4e91a52edbe7de2f1750f2e86","D13_starboard_commons_authored":"faf503cf2037d80d9fdfc3d046ccc153ce448635e049dd162036b087d1b06c76","D14_starboard_commons_authored":"8be8e337d57266e8e674c4bbd34ac4386d4668097234fa7b4a64b5ce43387aaa","D09_R070_and_connected_approach":"5c14f78f43921197814ee50cddcc8e10fdcd24e2e78c551940613d80c8b8dbd1","D01_arrivals_ground":"abe5a4b8e33769777c2f7e346584b170795d92a1d58d52a03246b24ffc9e8156","D02_fusion_visitor_galleries":"2b1aa0f991ad69a8cd9edd916ca08bf46dd35d84b612ef58eb926b1ead337478","D02_fusion_screened_service":"f39ce2c818d49907305ed5a5d508ff5bf8c842b7c3f4f2ad2d97c70e267c38a8","D03_protected_crew_cover":"fde5cae8a5bb216c2c7019d3bd9c49e4b8ba925f7186f7a1142f3e0ff3768507","D12_star_atlas_ground_0":"5fa6d266af0709b0fff7e2486690761f186601e034a8e37fc8f81c8933c1f93b","D13_star_atlas_gallery_0":"9f5c832b1ceb120c363b32e66e30330edd29b011e6308385238015a318dfffd6","D13_star_atlas_lower_roof_0":"a8612963bbc3d50fab363c29c99f4f8feef9f4c0804027ae9023ddbb275723bf","D14_star_atlas_gallery_0":"a241d4439e67f9f22bd9297396f4be1d90e72584b10c4f55629e233d45853628","D15_star_atlas_protected_cover_0":"fdf24ff3cbba4a3b46d840c0a4e7e870d22a338bf888b82f6419840e5e5eef39","D11_aquatic_cinema_interface":"17b54f8c238c202eb86e2417b8d43a914b8e7c1f7718debc7b5f54caebc71592","D11_aquatic_hall_cover":"1a36bb3d6034c9e5e37dd3f112e72246c516ac72c301f07b05a480684be8562d","D10_vesper_upper_dining":"84c442d3854a4669b10b60ed47fa353cf6e500fbafd4c82a63a144555998e59f","D15_starboard_house_extension":"969f291a568c252cfccbc4c1ef9565237ac03230f36c878da427ae3f0600114c","D16_starboard_house_extension":"4e764c53a28e5ca0fa726681c04ab57f8fafbe30d9ed92bf252792781ec73745","D17_starboard_house_extension":"08443f53f118d5c136f144b8a10216bc868e39676c967f08857dfeb84ec1bdd8","D18_starboard_house_cover":"f79ba99ebaabd0f8e165de9ef79701856f0b769f952f32e8d508f82832a26526","D09_thread_shell_floor":"9cbeeaa52215ce6d94f30faa56311a57008e4207f1ddfb2ec57e47a4b7317294","D10_thread_shell_cover":"d15a0154e90913bce124e54d5c30f26f2cb6dc51a45b55a97f97dcca23396e8b","D09_orchard_exchange_floor":"10aa4ad81de95ff1ae7e539aa966f0fe3eaec95085510f45a4d5917988c63256","D10_orchard_exchange_floor":"709f51587aa5a4fb1b6b65d1bc4be87cda1fd37681642ee14683018b1231cf58","D10_orchard_foodhall_floor":"bc19709534b61992b792b90e5a7df13bb5a8772468ca4da3d3dd3dd22ac72467","D01_primary_atrium_core_floor":"1c9b1fe69dc57c88d1fc0b4c64dbbd072b6567f463ef68db5579417d51fb5f1e","D02_primary_atrium_core_floor":"4c309af3eef25d9ec5d703b9f1f369fc2649db32f851212617436e099ba910d4","D03_primary_atrium_core_floor":"a2fea8ec875900f5757c2a363eed1678d27b793f6a6f922f15e23a1273f7a21f","D04_primary_atrium_core_floor":"c8b26fb5b5c83c7992947b9e90a500562d34bb4ff3869a6fb2860dc71ad8379f","D05_primary_atrium_core_floor":"23e6f4356ead5f730b97bc8c03bb689e37cd9a82a3729cc4cc70f4a6718e7216","D06_primary_atrium_core_floor":"9ebafa0a5da31252ac0725f8ad26d5b51b5ad86e756fa803426edb6e4092d017","D07_primary_atrium_core_floor":"bfd50454ddb1d1e3d9de28dbe36596e40930828e883f611737315259258195c5","D08_primary_atrium_core_floor":"747fa84c15cf863d38500c33b59e49d6cbad1a995e73c7b732c621b341a77fb2","D09_primary_atrium_core_floor":"de7039672772e6ce2ff3a4f9f36617160e7f7f22c02df7960d223111364c586b","D10_primary_atrium_core_floor":"f910bde04f5a9e8c024c0567d74d73df16affe77aa66a890f4af146f15b5d53c","D11_primary_atrium_core_floor":"aef3269fa31946b8f0d0a39417e8965deba3fbe09483a3e190aec1e94b884ab5","D12_primary_atrium_core_floor":"7e30924d695f39242009d5d63209f0c92f91e75e08bebf8c7720a42c23568692","D13_primary_atrium_core_floor":"541d3b92bf12d3513e3116662dff0f6092a5ce09a28ac0bb9b3566bac938f435","D14_primary_atrium_core_floor":"24129ba8aabb881971c0f01dd709bb9f084fe8104bb079ff0169008bc0e623f6","D15_primary_atrium_core_floor":"198911b53ccb05a2fa7b05353188d09501f5dc2df87857509a484fa0380f4754","D16_primary_atrium_core_floor":"6516a22fa839c6c55718188a662e33f497d174e3cd34f8275d00b242b2c89f09","D17_primary_atrium_core_floor":"02fbb0c1cf0493ebed0c7c563ffd758f0503777afbfa5b03446f81763c7306b4","D18_primary_atrium_core_floor":"c570eec12a8b84339f49bcbd3d21f389923957bc1242fffb2a06e00380a374b0","D17_aft_crown_link_floor":"43ed91b1822a5b871c5607950f2c6d81273fdea9806bf96cab36a22f902b49ea","D18_aft_crown_link_floor":"54e044c88c8923879ed42920e2cc3abacac4d0b2ab701027a6c05dd0c766cb4b","D01_forward_public_core_floor":"a1a219f05bfbdee9641fa378b7e2f1dcc52c76370e89506834d8baafbff9a10a","D02_forward_public_core_floor":"346a454ad5ec7a9f42099cf729112eb9ac8a121a20ccaf509f8397984e1248f8","D03_forward_public_core_floor":"64a058c06bde8722852fbcd7d30d776993f3ed80b0f11f66ea32b0538672f852","D04_forward_public_core_floor":"97eaf5dd9f441fd7efcb77b7ba485e114e162ee570da7a05582b741ff448e826","D05_forward_public_core_floor":"38af41d35aa73ee4322a3ea01a524d7053c9140d6b053784b719e363e391a4ad","D06_forward_public_core_floor":"beb8b28d6ff3db40e197c194b6c7d70a2490a5b8eaa996fc302581eabaac275d","D07_forward_public_core_floor":"368134f0c75d6fe6174a850083ffaf997ad1c5b22913f777f1bb66cea051e13d","D08_forward_public_core_floor":"e35fb3af519e1409c31ce3435f6f89f77f8a910993e6787a0d2a8357ea612ac4","D09_forward_public_core_floor":"462e7e595d16bff732323bf77ad3d20715edfe2376dcc2692706a46e8e8bead5","D10_forward_public_core_floor":"715ae8e2f58a312aca5398e675d47c3a81fa0795824b455c1068cb7f1d8203d0","D11_forward_public_core_floor":"df2fde0c494c99fc812b10d548d2799d214e93c57b51d03498da0613b4926ab4","D12_forward_public_core_floor":"a861a08fff00d735dd25ca9ccf3be8eee24258caaaf5d23ea54cefb8c460a6d5","D13_forward_public_core_floor":"be66ea4abc69aa4dab8da5906462b272be8ce4a619d6fc78d8c0e9ce47124bdf","D14_forward_public_core_floor":"a63194cc9b3cc1e236d50ffa269193b40cb4e6af1089f1c3637b79a7810105ef","D15_forward_public_core_floor":"5e93cabdac9a07429ccac177139253ce1f1879e26931c077f32b7cae072056b2","D16_forward_public_core_floor":"45cb3be2948b3e98e74fb15e3f9f77e25178bcede40920e59fe43a5a5a27da2e","D17_forward_public_core_floor":"2c1c4fe4510ece99dd8793cc6499d42c8525386ac60580b3734123095d86d5ea","D01_fore_midship_public_core_floor":"4c01dae3933b1298233d59a5c69c6a9f6b0ce35087d1462a45366fb8b5853fb0","D02_fore_midship_public_core_floor":"13afffe620b264eeb608c29b61440e3aa45b4ffd5f9a250b3bd4e534191de500","D03_fore_midship_public_core_floor":"2d5cdd2222a83ffe7075cd4d70142b46548f0ac60957c063dc6c4d293215be5b","D04_fore_midship_public_core_floor":"eaa1a8919fa7661ab63d7908a8ad735f20b3636881b74f607df8a4ce8e1e2595","D05_fore_midship_public_core_floor":"22569ba701e441200475569d57fa113a3226f78635e195b6b9770a19af561575","D06_fore_midship_public_core_floor":"3a9d1fe5097538a23deda871987a511e3060eba51cb7b90701cd791353b9db8f","D07_fore_midship_public_core_floor":"750ddf05605f586b7c7d4671eabf7668c3d1a63c51d71fe3e005390a08c2bb31","D08_fore_midship_public_core_floor":"b995e65ecb61343710748a4df8c90d3ef7fd1056152691e71f81c2be834b597c","D09_fore_midship_public_core_floor":"f85464acf7fb6690f6416da38174ac6fc9ba4c41bc001bdc6f51d6970efebbeb","D10_fore_midship_public_core_floor":"71041512e84c42409a0e10748247b52729394af0c1bfa1ecc29307d2e067e65c","D11_fore_midship_public_core_floor":"50bddad90d544753acafb8b599fbe099c100f1bd53187ab9171f52bc4b019806","D12_fore_midship_public_core_floor":"8d9264486984239b6d8ee902c647c1f7d69178d51cc838e66d16d31abf5bcf22","D13_fore_midship_public_core_floor":"8a5cf0c65263027baba42259973973f1a6810665c9c32c9acf9f0a8741e764e9","D14_fore_midship_public_core_floor":"0418388c3247941f8e75b45ab2cafe5f9e83d0cfc935b8c40eb761ea4c1e1c30","D15_fore_midship_public_core_floor":"55a2a49d949ad6b6d9f97dcc4e0dceb4735372e55f8f5bec224ea9ec987f99e3","D16_fore_midship_public_core_floor":"d607c4c7a61d194428b0ce24a50f03d2d5939959a29c74f58ab6f1a938f6067b","D17_fore_midship_public_core_floor":"da2769d723dd7d43f916047233688db3210717293c0d3389e7de76a73052e66e","D01_aft_midship_public_core_floor":"c26c86229c128a17d9714199582ff52e5780a009f8a7f4513c1663157722f144","D02_aft_midship_public_core_floor":"e3e1773dcfc360541d01a4ae97daffd5f563176a92ef031b0824bd9daa0dec5d","D03_aft_midship_public_core_floor":"b1311724888cb65099d7e27b8a703a850779fcb63d7551e48ac342543c2cf938","D04_aft_midship_public_core_floor":"afefbb5c95842601b4e1efe1ddfa8c34b0235c8d323a99cc9a6df26e972f4e78","D05_aft_midship_public_core_floor":"c0a6894be49d908c0707e46f54e2d2b47a70c3eb9adce10c0d2ce87de6708fa2","D06_aft_midship_public_core_floor":"2a221619573f13a419584f00de8c6f61c16d57e334d9f7d0f2569508c9ef9385","D07_aft_midship_public_core_floor":"4d40f09bc855fc4dfdd2f8a9b316114f64905642815d61c2712c100faf972d61","D08_aft_midship_public_core_floor":"9f3e28938916976a0cd40c98a1c45ceee5dcde0075d31a96b208260dc763d93c","D09_aft_midship_public_core_floor":"84acf31d16c328088971d73f7a9c2a3a5e432d61ada800a76337306226659ccf","D10_aft_midship_public_core_floor":"9db2f2a2280a0c9b9794aead007df9a21887b2d417edfe6f378ecb36ebf667b3","D11_aft_midship_public_core_floor":"afbacc5d2b1cdc6b9b6088445ec6540592a7a19714b28a1b23a144500745b81c","D12_aft_midship_public_core_floor":"a200c5db015b159257fea9f73cd9785498831dc3c322be855060a6ab875939af","D13_aft_midship_public_core_floor":"75e304266751d642e1dbeb816d6fd8f34413aa4584ed49ab0d540bf9a9399b60","D14_aft_midship_public_core_floor":"8e64c24fe18ac5b258c57c086f7c993a7a6b98f19e85fe6cb1d57f7f85f0306c","D15_aft_midship_public_core_floor":"5650e2b25f160b592e64c2745335c37f3061ad30bbfd52cfa7098a627b7f7343","D16_aft_midship_public_core_floor":"d00c1eb9a8a6fcec3ef2493e7cd58d8b8c4d36020d8030787855571cd54ea38f","D17_aft_midship_public_core_floor":"5310b7615ab3407ee07aca2221425f57b9b753c665c0ed2bf543f25d23fe93cf","D01_aft_public_core_floor":"78754b10e2709d171cc6ce3a006d7796525a04c79b28de0fb19000ab1a318301","D02_aft_public_core_floor":"ab5f62fc4747dde215e8941989e0b163a41cb49626e1fa12e5b090d35bb99f86","D03_aft_public_core_floor":"1e6522ff7435c99fa1fda7d2e76cc4210df18a289bffa081be64af414718304b","D04_aft_public_core_floor":"ef43ff48c75791ea7eddf32aca872602d061f74170d7ac86716036996266306f","D05_aft_public_core_floor":"dc739013dc72eb2fc07274cd4e9d1881f1ceb7d12f2db2240b0baa674790f667","D06_aft_public_core_floor":"b00002bdda9fa02adc78ccbe0760887b39059b79cf9c69aff1eb2360b6066944","D07_aft_public_core_floor":"18d254399e24e469735aa47efef483a405adef7cdcbd09e7a9e92af9bd556a10","D08_aft_public_core_floor":"411ae947951adfbe095e8c75bfa47cfd3a5ec316a0c851e476d6b1e24616205b","D09_aft_public_core_floor":"851e134d1ab63f8c2c0931e10ca79179eefc57ae5d6b2d9c126579a36631dada","D10_aft_public_core_floor":"5cb698bcaff3d77160c587598dd11f93d84b6aaf95cf06c0c0974faa10dbc79d","D11_aft_public_core_floor":"08e61fb2809f982b372c20a016f55931a1e8bfba396a619f61444f9d2a79d2a1","D12_aft_public_core_floor":"629c76af02f523d3e1bb6018c90ff03721735a755acee18140e050135dfdafba","D13_aft_public_core_floor":"b72f4699c488e38fd6dc384e8a861f9e818ec1cda7fbf3df260be7c7f7146172","D14_aft_public_core_floor":"ca8e5fb6a59d1a63bb80de0e460d449ebadca69f4adbea0658aa92b7ebd32e70","D15_aft_public_core_floor":"0435228033e04191e9eed5375264bd67da7818306158e4065e43110691e7a638","D16_aft_public_core_floor":"119c8cc07bb5763d81455cca76a251e062f8facdf3f3733a9546ed9401eb2167","D17_aft_public_core_floor":"ee934ba3c2739d7353c16ca76a6611abe3ae4e9cc42e2c4bcab68959dd699271","D01_port_forward_staff_floor_0":"8a5f8184af3379175224f611d3d534ac853e87c65f5a7f7212e32eed70bcc779","D02_port_forward_staff_floor_0":"59b0c3b352b322ea87385a49eabae756373fc08f56bc68af9709bf720fe5f00b","D03_port_forward_staff_floor_0":"65cef62f8a0a704dbdbb00425a38454352b685110d82106e5d41fbe7bfe33c3b","D18_aft_command_port_floor":"85c69cf58982614bd2d7f6b8f162a5a2678fe0c90761798d88d22d07636e28f2","D18_aft_command_starboard_floor":"b21d5ba3582475ca2a9e5a5627fcd2222c85e6fb857a762a3a8f96484e0d5f50","D18_bridge_platform_port_wing":"1daf06b9b775670f7865697ad208ae7f9c9db400db15dc0c7c2d7960818df62c","D18_bridge_platform_starboard_wing":"e128063dba72e9bce166d4cc9f9455e66782e115e4c3fb6ceea3a48ba7946741","D18_bridge_platform_public_bypass":"9455de8ae60af62a9596ff288963ecbb85d684a79e188f4d7b37cdaef883725f"}"""
var failures: Array[String] = []
var ship: Node3D
var shell: Node3D
var platform: Node3D
var floors: Node3D
var space: PhysicsDirectSpaceState3D
var dynamic_exclusions: Array[RID] = []
var shell_exclusions: Array[RID] = []
var own_exclusions: Array[RID] = []
var slab_exclusions: Array[RID] = []
var gltf: Dictionary
var binary: PackedByteArray
var matched_triangles := 0
var maximum_corner_error := 0.0
var pier_slices := 0
var keel_rays := 0
var floor_owners := 0
var maximum_floor_corner_error := 0.0
var matched_floor_triangles := 0
var bearing_witnesses := 0
const PINS := {"assets/models/AST-CMD-002.glb":"3577d49136b0252f8eef677604ef85488b92913580c8f8a034b947120a70a0ea","data/generated/structural_meshes.json":"1427634f9531fcdfec73b26e9e20343794d35d216991a4d4054005f1099e3e90","data/spatial_layout.json":"8560fa088ea15109e8539afbc9bed52732ebbe109956508c315e4a71995253be","docs/AFT_CROWN_PLATFORM_SOURCE_CONTACT_AUDIT.json":"02afb1e3ce0822a6620ef5f0f5602da206ada97e86eadd02056bb6983e40e9ad","data/architecture/UPPER_HORIZON_ENCLOSURE_RUNTIME.json":"08fac10329f0a58661daa5e69b1f345c58386be130e10d8c3e215d09a8bb5880","docs/UPPER_HORIZON_ENCLOSURE_SOURCE_CONTACTS.json":"09b9f786ccc57359cec19f183dcc1451cc85343d4714bc2853c78261f18a8398","docs/UPPER_HORIZON_ENCLOSURE_SOURCE_ROUNDTRIP.json":"2d1b9adcd64b827686099c2b283f9408c2a822c930b8f724e0cc8b866eef9c42","data/architecture/UPPER_HORIZON_ENCLOSURE_GEOMETRY_PARTS.json":"d070ab3cec5cb2b2563f08cb79a741be728dd66f93310338f36fccc5f588548e","assets/models/AST-CMD-005.glb":"323a26fe17cb9d6bd652309c0a4c99e4d1ce2d3316526b4d125d732dec0c0cf6","assets/models/AST-CMD-006.glb":"70fd0d75fba5a61f0f59dddc9a00e86fdb88828acf7379f7838e7e2db5fc1860","data/architecture/AFT_CROWN_PLATFORM_RUNTIME.json":"b6692962f2c4a477827acbb685542b79aa0e09ef513ee6445ed840aefbf79011"}

func _initialize() -> void:
	call_deferred("run")

func check(ok: bool, detail: String) -> bool:
	if not ok:
		failures.append(detail)
		push_error(detail)
	return ok

func read_json(path: String) -> Dictionary:
	var value: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	if not check(value is Dictionary, "Missing/malformed JSON: " + path):
		return {}
	return value

func v3(a: Array) -> Vector3:
	return Vector3(float(a[0]),float(a[1]),float(a[2]))

func ray(a: Vector3, b: Vector3, exclusions: Array[RID]) -> Dictionary:
	var q := PhysicsRayQueryParameters3D.create(a,b)
	q.exclude = exclusions
	return space.intersect_ray(q)

func accessor(index: int) -> Array:
	var a: Dictionary = gltf.accessors[index]
	var view: Dictionary = gltf.bufferViews[int(a.bufferView)]
	var width := 3 if str(a.type) == "VEC3" else 1
	var component := int(a.componentType)
	var size := 2 if component == 5123 else 4
	check(component in [5123,5125,5126] and not a.has("sparse"),"Unsupported raw GLB accessor")
	var start := int(view.get("byteOffset",0))+int(a.get("byteOffset",0))
	var stride := int(view.get("byteStride",width*size))
	var result: Array = []
	for i in range(int(a.count)):
		var offset := start+i*stride
		if width == 3:
			result.append(Vector3(binary.decode_float(offset),binary.decode_float(offset+4),binary.decode_float(offset+8)))
		else:
			result.append(binary.decode_u16(offset) if component == 5123 else binary.decode_u32(offset))
	return result

func raw_batches() -> Dictionary:
	var bytes := FileAccess.get_file_as_bytes(asset_path)
	if not check(bytes.size() > 28 and bytes.decode_u32(0) == 0x46546c67 and bytes.decode_u32(4) == 2,"Invalid GLB container"):
		return {}
	var length := int(bytes.decode_u32(12))
	gltf = JSON.parse_string(bytes.slice(20,20+length).get_string_from_utf8())
	var bin_start := 20+length
	check(bytes.decode_u32(bin_start+4) == 0x004e4942,"Expected GLB binary chunk")
	binary = bytes.slice(bin_start+8,bin_start+8+int(bytes.decode_u32(bin_start)))
	var result: Dictionary = {}
	for node in gltf.nodes:
		if not node.has("mesh"):
			continue
		# Reviewed export bakes world transforms. Refuse a changed hierarchy rather
		# than silently comparing local coordinates to world-space runtime data.
		check(not node.has("matrix") and not node.has("translation") and not node.has("rotation") and not node.has("scale") and not node.has("children"),"Unreviewed GLB transform/hierarchy")
		var faces := PackedVector3Array()
		for primitive in gltf.meshes[int(node.mesh)].primitives:
			check(int(primitive.get("mode",4)) == 4,"GLB primitive is not triangles")
			var positions := accessor(int(primitive.attributes.POSITION))
			var indices := accessor(int(primitive.indices))
			for index in indices:
				faces.append(positions[int(index)])
		result[str(node.name)] = faces
	return result

func triangle_error(source: PackedVector3Array, a: int, imported: PackedVector3Array, b: int) -> float:
	var best := INF
	# glTF CCW -> Godot clockwise conversion; cyclic permutations preserve the
	# required orientation. A reflected/reversed triangle is never accepted.
	for rotation in range(3):
		var error := 0.0
		for corner in range(3):
			error = maxf(error,source[a+corner].distance_to(imported[b+(rotation-corner+3)%3]))
		best = minf(best,error)
	return best

func validate_meshes(roundtrip: Dictionary) -> void:
	var batches := raw_batches()
	var meshes := shell.find_children("*","MeshInstance3D",true,false)
	check(meshes.size() == batches.size() and meshes.size() == expected_batches,"Exact bounded source batch census differs")
	var minimum := Vector3(INF,INF,INF)
	var maximum := Vector3(-INF,-INF,-INF)
	for item in meshes:
		var mesh := item as MeshInstance3D
		if not check(batches.has(str(mesh.name)) and mesh.mesh != null and mesh.is_visible_in_tree(),"Missing source batch or invisible runtime mesh: "+str(mesh.name)):
			continue
		var source: PackedVector3Array = batches[str(mesh.name)]
		batches.erase(str(mesh.name))
		var local_faces := mesh.mesh.get_faces()
		var faces := PackedVector3Array()
		for vertex in local_faces:
			var point: Vector3 = mesh.global_transform*vertex
			faces.append(point)
			minimum = minimum.min(point)
			maximum = maximum.max(point)
		var contact := mesh.get_node_or_null("StaticContact/SharedShape") as CollisionShape3D
		if check(contact != null and not contact.disabled,"Missing active collision: "+str(mesh.name)):
			check(contact.shape is ConcavePolygonShape3D and contact.get_parent() is StaticBody3D and contact.get_parent().collision_layer != 0,"Wrong static collision type/layer")
			if contact.shape is ConcavePolygonShape3D:
				check(contact.shape.get_faces() == local_faces and contact.global_transform.is_equal_approx(mesh.global_transform),"Exact imported render/collision mismatch: "+str(mesh.name))
		if not check(source.size() == faces.size(),"Source/runtime triangle multiplicity differs: "+str(mesh.name)):
			continue
		var used: Dictionary = {}
		for a in range(0,source.size(),3):
			var found := -1
			var best := EPS
			for b in range(0,faces.size(),3):
				if used.has(b):
					continue
				var error := triangle_error(source,a,faces,b)
				if error < best:
					best = error
					found = b
			if check(found >= 0,"No one-to-one oriented source triangle: %s/%d" % [mesh.name,a/3]):
				used[found] = true
				matched_triangles += 1
				maximum_corner_error = maxf(maximum_corner_error,best)
	check(batches.is_empty(),"Source batches absent from runtime")
	check(matched_triangles == int(roundtrip.get("triangles",-1)),"Full immutable source triangle coverage incomplete")
	check(maximum.y <= 114.5+EPS,"Architecture exceeds114.5m exterior limit")
	if expected_batches==448:
		check(minimum.y>=106.5-EPS,"New enclosure descends below fixed slab")

func vertex_key(point: Vector3) -> String:
	return "%d,%d,%d" % [roundi(point.x * 1000), roundi(point.y * 1000), roundi(point.z * 1000)]

func geometry_signature(faces: PackedVector3Array) -> String:
	var triangles := PackedStringArray()
	for index in range(0, faces.size(), 3):
		var corners := PackedStringArray()
		for offset in range(3):
			corners.append(vertex_key(faces[index + offset]))
		corners.sort()
		triangles.append("|".join(corners))
	triangles.sort()
	return "\n".join(triangles).sha256_text()

func box_hits(bounds: AABB, excluded: Array[RID], label: String) -> Array[Dictionary]:
	var shape := BoxShape3D.new()
	shape.size = bounds.size
	var query := PhysicsShapeQueryParameters3D.new()
	query.shape = shape
	query.margin = 0.0005
	query.transform.origin = bounds.get_center()
	query.exclude = excluded
	var hits := space.intersect_shape(query, MAX_RESULTS)
	check(hits.size() < MAX_RESULTS, "Query capacity saturated: " + label)
	return hits

func owner(hit: Dictionary) -> String:
	return "<no contact>" if hit.is_empty() else str(hit.collider.get_path())

func region_id(body: Node) -> String:
	var node := body
	while node != null:
		if node.has_meta("region_id"):
			return str(node.get_meta("region_id"))
		node = node.get_parent()
	return ""

func assert_empty(bounds: AABB, exclusions: Array[RID], label: String) -> void:
	for hit in box_hits(bounds, exclusions, label):
		check(false, label + " -> " + owner(hit))

func append_floor_face(faces: PackedVector3Array,a: Vector3,b: Vector3,c: Vector3,normal: Vector3) -> void:
	# Source compiler describes geometry; reconstruct the builder's outward
	# clockwise convention explicitly rather than discarding triangle winding.
	if (b-a).cross(c-a).dot(normal)>0.0:
		var swap := b
		b = c
		c = swap
	faces.append_array(PackedVector3Array([a,b,c]))

func compiled_faces(region: Dictionary, rendered: bool = false) -> PackedVector3Array:
	var faces := PackedVector3Array()
	var top := float(region.floor_y)
	var thickness := float(region.thickness)
	var chunks: Array = region.get("render_chunks",[])
	for triangle in region.triangles:
		var a := Vector3(triangle[0][0],top,triangle[0][1])
		var b := Vector3(triangle[1][0],top,triangle[1][1])
		var c := Vector3(triangle[2][0],top,triangle[2][1])
		if not rendered or chunks.is_empty():
			append_floor_face(faces,a,b,c,Vector3.UP)
		append_floor_face(faces,a-Vector3.UP*thickness,b-Vector3.UP*thickness,c-Vector3.UP*thickness,Vector3.DOWN)
	if rendered:
		for chunk in chunks:
			for triangle in chunk.triangles:
				append_floor_face(faces,Vector3(triangle[0][0],top,triangle[0][1]),Vector3(triangle[1][0],top,triangle[1][1]),Vector3(triangle[2][0],top,triangle[2][1]),Vector3.UP)
	for ring in region.rings:
		for index in range(ring.size()):
			var p: Array = ring[index]
			var q: Array = ring[(index+1)%ring.size()]
			var a := Vector3(p[0],top,p[1])
			var b := Vector3(q[0],top,q[1])
			var c := b-Vector3.UP*thickness
			var d := a-Vector3.UP*thickness
			var direction := b-a
			var normal := Vector3(direction.z,0,-direction.x).normalized()
			append_floor_face(faces,a,b,c,normal)
			append_floor_face(faces,a,c,d,normal)
	return faces

func match_floor_faces(expected: PackedVector3Array,actual: PackedVector3Array,label: String) -> bool:
	if not check(expected.size()==actual.size(),"Floor triangle multiplicity differs: "+label):
		return false
	var used: Dictionary = {}
	var ok := true
	var local_max := 0.0
	for a in range(0,expected.size(),3):
		var found := -1
		var best := EPS
		var best_rotation := -1
		var centre := (expected[a]+expected[a+1]+expected[a+2])/3.0
		for b in range(0,actual.size(),3):
			if used.has(b) or centre.distance_to((actual[b]+actual[b+1]+actual[b+2])/3.0)>EPS:
				continue
			# Both arrays use Godot clockwise winding. Cyclic permutations only;
			# reversed faces cannot satisfy this oriented multiplicity-preserving match.
			for rotation in range(3):
				var error := 0.0
				for corner in range(3):
					error = maxf(error,expected[a+corner].distance_to(actual[b+(rotation+corner)%3]))
				if error<best:
					best = error
					found = b
					best_rotation = rotation
		if not check(found>=0,"Unmatched oriented floor triangle: "+label+" #"+str(a/3)):
			ok = false
			continue
		used[found] = true
		matched_floor_triangles += 1
		local_max = maxf(local_max,best)
		maximum_floor_corner_error = maxf(maximum_floor_corner_error,best)
		if label=="D09_living_gifts_floor render":
			for corner in range(3):
				var p := expected[a+corner]
				var q := actual[found+(best_rotation+corner)%3]
				if absf(p.z-192.545454545)<0.0001:
					print("LIVING GIFTS UNROUNDED CORNER expected(%.9f,%.9f,%.9f) actual(%.9f,%.9f,%.9f) error%.9fm" % [p.x,p.y,p.z,q.x,q.y,q.z,p.distance_to(q)])
	if local_max>0.0001:
		print("FLOOR MATCH "+label+" max actual corner error %.9fm" % local_max)
	return ok and used.size()*3==expected.size()

# Nine-decimal numerical record equality complements the Python byte-equivalent
# retained-record planning receipt; numeric int/float formatting is normalized.

func canonical(value: Variant) -> String:
	if value is Dictionary:
		var keys: Array = value.keys()
		keys.sort()
		var fields := PackedStringArray()
		for key in keys:
			fields.append(JSON.stringify(str(key))+":"+canonical(value[key]))
		return "{"+",".join(fields)+"}"
	if value is Array:
		var fields := PackedStringArray()
		for item in value:
			fields.append(canonical(item))
		return "["+",".join(fields)+"]"
	if value is float or value is int:
		return "%.9f" % float(value)
	return JSON.stringify(value)

func slab_witness(point: Vector2, label: String, expected_id: String = "") -> void:
	var top := ray(Vector3(point.x,106.6,point.y),Vector3(point.x,106.4,point.y),slab_exclusions)
	var bottom := ray(Vector3(point.x,106.1,point.y),Vector3(point.x,106.4,point.y),slab_exclusions)
	check(not top.is_empty() and region_id(top.collider) in FLOOR_IDS and (expected_id.is_empty() or region_id(top.collider)==expected_id) and absf(top.position.y-FLOOR_Y)<EPS,label+": actual new slab top missing -> "+owner(top))
	check(not bottom.is_empty() and region_id(bottom.collider) in FLOOR_IDS and (expected_id.is_empty() or region_id(bottom.collider)==expected_id) and absf(bottom.position.y-SLAB_BOTTOM)<EPS,label+": actual new slab underside missing -> "+owner(bottom))

func floor_face_diagnostic(label: String,expected: PackedVector3Array,actual: PackedVector3Array) -> void:
	var expected_keys: Dictionary = {}
	var actual_keys: Dictionary = {}
	for row in [[expected,expected_keys],[actual,actual_keys]]:
		var faces: PackedVector3Array = row[0]
		var keys: Dictionary = row[1]
		for index in range(0,faces.size(),3):
			var corners := PackedStringArray([vertex_key(faces[index]),vertex_key(faces[index+1]),vertex_key(faces[index+2])])
			corners.sort()
			var key := "|".join(corners)
			keys[key] = int(keys.get(key,0))+1
	print("FLOOR DIAGNOSTIC "+label+" expected/actual triangles "+str(expected.size()/3)+"/"+str(actual.size()/3))
	var printed := 0
	for key in expected_keys:
		if int(expected_keys[key])!=int(actual_keys.get(key,0)) and printed<6:
			print("EXPECTED DIFF "+str(key)+" multiplicity "+str(expected_keys[key])+"/"+str(actual_keys.get(key,0)))
			printed += 1
	printed = 0
	for key in actual_keys:
		if int(actual_keys[key])!=int(expected_keys.get(key,0)) and printed<6:
			print("ACTUAL DIFF "+str(key)+" multiplicity "+str(expected_keys.get(key,0))+"/"+str(actual_keys[key]))
			printed += 1

func validate_floors() -> void:
	var generated := read_json("res://data/generated/structural_meshes.json")
	var layout := read_json("res://data/spatial_layout.json")
	var old_hashes: Dictionary = JSON.parse_string(OLD_RECORD_HASHES_JSON)
	check(generated.regions.size()==249 and old_hashes.size()==245,"Exactly249 owners with245 retained compiled records required")
	var owned: Array = layout.regions.filter(func(row:Dictionary)->bool:return str(row.get("authoring_owner",""))=="aft_crown_platform")
	check(owned.size()==4,"Exactly four authored platform regions required")
	for row in owned:
		check(str(row.id) in FLOOR_IDS and int(row.priority)==-10,"Infill must retain four approved low-priority owners")
	var seen: Dictionary = {}
	var new_area := 0.0
	for region in generated.regions:
		var id := str(region.id)
		check(not seen.has(id),"Duplicate floor identity: "+id)
		seen[id] = true
		if old_hashes.has(id):
			check(canonical(region).sha256_text()==str(old_hashes[id]),"Retained compiled record changed: "+id)
		else:
			var index := FLOOR_IDS.find(id)
			if not check(index>=0,"Unapproved new floor owner: "+id):
				continue
			check(absf(float(region.floor_y)-FLOOR_Y)<EPS and absf(float(region.thickness)-0.24)<EPS,"New slab datum/thickness changed: "+id)
			check(absf(float(region.structural_area_m2)-[1154.6,1154.6,1604.0,1604.0][index])<EPS,"New slab area changed: "+id)
			new_area += float(region.structural_area_m2)
		var slab := floors.get_node_or_null(id) as Node3D
		if not check(slab!=null,"Actual retained/new floor owner absent: "+id):
			continue
		var render := PackedVector3Array()
		var contact := PackedVector3Array()
		for item in slab.find_children("*","MeshInstance3D",true,false):
			var mesh := item as MeshInstance3D
			if check(mesh.mesh!=null and mesh.is_visible_in_tree(),"Invisible/missing floor mesh: "+id):
				for p in mesh.mesh.get_faces():
					render.append(mesh.global_transform*p)
		for item in slab.find_children("*","CollisionShape3D",true,false):
			var shape := item as CollisionShape3D
			if check(not shape.disabled and shape.shape is ConcavePolygonShape3D,"Invalid floor contact: "+id):
				for p in shape.shape.get_faces():
					contact.append(shape.global_transform*p)
		var expected_contact := compiled_faces(region)
		var expected_render := compiled_faces(region,true)
		var contact_ok := match_floor_faces(expected_contact,contact,id+" collision")
		var render_ok := match_floor_faces(expected_render,render,id+" render")
		if not contact_ok:
			floor_face_diagnostic(id+" collision",expected_contact,contact)
		if not render_ok:
			floor_face_diagnostic(id+" render",expected_render,render)
		check(render_ok and contact_ok,"Actual full slab triangles/multiplicity differ from compiled owner: "+id)
		floor_owners += 1
		if id in FLOOR_IDS:
			for triangle in region.triangles:
				var p := Vector2.ZERO
				for corner in triangle:
					p += Vector2(float(corner[0]),float(corner[1]))/3.0
				slab_witness(p,"Compiled triangle "+id,id)
				# Concave trimeshes are hollow; centre probes outside the slab
				# while crossing its outward top/underside face.
				for y in [106.505,106.255]:
					var hits := box_hits(AABB(Vector3(p.x-0.01,y-0.015,p.y-0.01),Vector3(0.02,0.03,0.02)),slab_exclusions,"Unique floor ownership "+id)
					var owners := PackedStringArray()
					for hit in hits:
						owners.append(region_id(hit.collider))
					check(hits.size()==1 and region_id(hits[0].collider)==id,"Duplicate/missing real compiled owner: "+id+" y"+str(y)+" actual owners "+str(owners))
	check(floor_owners==249 and absf(new_area-5517.2)<EPS,"All249 physical owners and5517.2m2 new floor required")

func validate_piers(data: Dictionary) -> void:
	check(data.support.pier_centres_xz.size()==6,"Six approved piers required")
	for index in range(6):
		var centre: Vector2 = PIER_CENTRES[index]
		var declared: Array = data.support.pier_centres_xz[index]
		check(Vector2(float(declared[0]),float(declared[1])).distance_to(centre)<EPS,"Approved pier position changed")
		for datum in [["base",-3.2],["head",114.0]]:
			var name := "DATUM_aft_platform_pier_%02d_%s" % [index+1,datum[0]]
			var marker := shell.find_child(name,true,false) as Node3D
			check(marker!=null and marker.global_position.distance_to(Vector3(centre.x,float(datum[1]),centre.y))<EPS,"Pier source datum missing/moved: "+name)
		for segment in range(16):
			var low := lerpf(-3.19,114.0,segment/16.0)
			var high := lerpf(-3.19,114.0,(segment+1)/16.0)
			var bounds := AABB(Vector3(centre.x-0.4,low,centre.y-0.6),Vector3(0.8,high-low,1.2))
			var label := "pier%d slice%d" % [index+1,segment]
			var y := (low+high)*0.5
			var hit := ray(Vector3(centre.x-1,y,centre.y+0.17),Vector3(centre.x+1,y,centre.y+0.17),shell_exclusions)
			# Highest slice can meet its positively seated transfer flange first;
			# below111m there is no frame allowance. No whole-batch exclusion.
			check(not hit.is_empty() and absf(hit.position.x-(centre.x-0.4))<EPS,"Actual full-height pier chord missing: "+label)
			pier_slices += 1
		for offset in [Vector2.ZERO,Vector2(-0.35,-0.55),Vector2(-0.35,0.55),Vector2(0.35,-0.55),Vector2(0.35,0.55)]:
			var start := Vector3(centre.x+offset.x,-3.0,centre.y+offset.y)
			var hit := ray(start,start-Vector3.UP*0.4,own_exclusions)
			check(not hit.is_empty() and "HUL_KeelPan" in owner(hit) and absf(hit.position.y+3.2)<EPS and hit.normal.y>0.999,"Actual keel centre/corner bearing absent: "+str(start))
			keel_rays += 1
		var base := ray(Vector3(centre.x,-3.25,centre.y+0.17),Vector3(centre.x,-3.1,centre.y+0.17),shell_exclusions)
		check(not base.is_empty() and absf(base.position.y+3.2)<EPS,"Actual pier/keel base gap")
	check(pier_slices==96 and keel_rays==30,"All96 installed slices and30 keel bearings must execute")

func validate_core() -> void:
	var core := ship.find_child("AftCrownLink_WIP",true,false) as Node3D
	check(core!=null and ship.find_child("AftCrownLift",true,false)!=null,"Existing aft core/lift identity missing")
	var core_data := read_json("res://data/architecture/AFT_CROWN_LINK.json")
	# JSON numbers are floats; Array equality also compares Variant types.
	check(core_data.origin.size()==3 and v3(core_data.origin).distance_to(Vector3(0,102,119))<EPS and core_data.lift.cap_y.size()==2 and absf(float(core_data.lift.cap_y[0])-109.73)<EPS and absf(float(core_data.lift.cap_y[1])-109.85)<EPS and core_data.stairs.size()==1,"Protected core datums changed")
	for p in [Vector2(0,113),Vector2(-1.5,111.5),Vector2(1.5,114.5)]:
		var hit := ray(Vector3(p.x,110.0,p.y),Vector3(p.x,109.7,p.y),own_exclusions)
		check(not hit.is_empty() and core.is_ancestor_of(hit.collider) and absf(hit.position.y-109.85)<EPS,"Protected actual shaft cap missing/moved")
	var layout := read_json("res://data/spatial_layout.json")
	for spec in [["aft_crown_link_lift",[-1.82,1.82,110.98,115.02],["D17","D18"]],["aft_crown_link_stairs",[-3.1,3.1,123.0,133.7],["D18"]]]:
		var matches: Array = layout.voids.filter(func(row:Dictionary)->bool:return str(row.id)==str(spec[0]))
		if not check(matches.size()==1,"Protected aft hole missing/duplicated"):
			continue
		var a: Array = spec[1]
		var opening: Dictionary = matches[0]
		check(opening.decks==spec[2],"Protected opening deck identities changed")
		var corners: Dictionary = {Vector2(a[0],a[2]):true,Vector2(a[1],a[2]):true,Vector2(a[1],a[3]):true,Vector2(a[0],a[3]):true}
		for p in opening.boundary:
			corners.erase(Vector2(p[0],p[1]))
		check(corners.is_empty() and opening.boundary.size()==4,"Protected hole footprint changed")
		for deck in opening.decks:
			var y := 102.0 if str(deck)=="D17" else 106.5
			assert_empty(AABB(Vector3(a[0]+0.02,y-0.3,a[2]+0.02),Vector3(a[1]-a[0]-0.04,0.32,a[3]-a[2]-0.04)),slab_exclusions,"Protected compiled floor opening")

func validate_fixtures(data: Dictionary) -> void:
	check(data.light_markers.size()==25 and shell.find_children("DATUM_light_*","Node3D",true,false).size()==25,"Exactly25 source fixtures required")
	var lights := platform.find_children("*","SpotLight3D",true,false)
	check(lights.size()==25,"Exactly25 runtime source-backed lights required")
	for item in data.light_markers:
		var marker := shell.find_child(str(item.name),true,false) as Node3D
		var p := v3(item.position)
		check(marker!=null and marker.global_position.distance_to(p)<EPS,"Source fixture marker moved/missing")
		var matches := 0
		for light in lights:
			if light.global_position.distance_to(p)<EPS:
				matches += 1
				check((-light.global_basis.z).dot(Vector3.DOWN)>0.999,"Source fixture aim changed")
		check(matches==1,"Exactly one light must use each source fixture")
		for offset in [Vector3.ZERO,Vector3(-0.05,0,0),Vector3(0.05,0,0),Vector3(0,0,-0.05),Vector3(0,0,0.05)]:
			var q: Vector3 = p+offset
			check(ray(q,q+Vector3.DOWN*0.25,dynamic_exclusions).is_empty(),"Fixture lens exit obstructed: "+str(item.name))
			var lens := ray(q,q+Vector3.UP*0.08,dynamic_exclusions)
			check(not lens.is_empty() and shell.is_ancestor_of(lens.collider),"Real source lens absent: "+str(item.name))

func validate_contacts(data: Dictionary, audit: Dictionary, geometry: Dictionary) -> void:
	check(bool(audit.get("pass",false)) and int(audit.part_count)==598 and bool(audit.new_parts_all_connected_to_six_old_piers),"Final rooted contact proof absent/failed")
	check(str(audit.source_sha256)=="0b892eb5b59111bea434d4a3c3c1c886fd8995511641c6f2e6f89c997ac9ab34","Contact source identity changed")
	var parts: Dictionary = {}
	var glass: Dictionary = {}
	for part in geometry.parts:
		check(not parts.has(str(part.name)),"Duplicate individual source solid")
		parts[str(part.name)] = part
		if str(part.group)=="glass":
			glass[str(part.name)] = true
		var bounds: Array = part.world_aabb
		check(float(bounds[2])>=106.5-EPS and float(bounds[3])<=114.5+EPS,"New solid violates retained floor/exterior datums")
		if str(part.group) in ["shoulder","shoulder_support"]:
			check(float(bounds[2])>=113.4-EPS,"High shoulder support lowered into view corridor")
		var centre := Vector2.ZERO
		for p in part.footprint_xz:
			centre += Vector2(p[0],p[1])/float(part.footprint_xz.size())
		# Probe both actual outward faces of every individual authored solid.
		# No opaque mesh/batch is exempted from geometric coverage.
		for face in [[float(bounds[2]),-1.0],[float(bounds[3]),1.0]]:
			var point := Vector3(centre.x,float(face[0]),centre.y)
			var delta := Vector3.UP*float(face[1])*0.004
			var hit := ray(point+delta,point-delta,enclosure_exclusions)
			check(not hit.is_empty() and hit.position.distance_to(point)<EPS,"Actual source solid face absent: "+str(part.name)+" y"+str(face[0]))
			solid_witnesses += 1
		# New floor-seated walls must meet an actual retained compiler slab.
		if absf(float(bounds[2])-FLOOR_Y)<EPS:
			var hit := ray(Vector3(centre.x,106.51,centre.y),Vector3(centre.x,106.24,centre.y),slab_exclusions)
			check(not hit.is_empty() and absf(hit.position.y-FLOOR_Y)<EPS and region_id(hit.collider) in FLOOR_IDS,"New wall lacks actual fixed-floor bearing: "+str(part.name))
			bearing_witnesses += 1
	check(parts.size()==598 and solid_witnesses==1196,"Complete individual closed-solid witnesses required")
	var roots: Dictionary = {}
	var old_audit := read_json("res://docs/AFT_CROWN_PLATFORM_SOURCE_CONTACT_AUDIT.json")
	for part in old_audit.root_pier_parts:
		roots[str(part.name)] = true
	check(roots.size()==24 and int(audit.old_root_part_count)==24,"Only six retained keel-bearing piers may root enclosure")
	# The enclosure has no new slab: its retained six-pier frame still bears the
	# same four compiled floor infills at every independently measured witness.
	for row in old_audit.slab_witnesses:
		check(float(row.plan_contact_area_m2)>0.00000001 and float(row.vertical_overlap_m)>0.001 and roots.has(str(row.root_pier_part)),"Retained slab support is not a positive rooted bearing")
		var ids := {"foyer_0":FLOOR_IDS[0],"foyer_1":FLOOR_IDS[1],"upper_horizon_0":FLOOR_IDS[2],"upper_horizon_1":FLOOR_IDS[3]}
		slab_witness(Vector2(row.sample_xz[0],row.sample_xz[1]),"Rooted slab bearer "+str(row.part),str(ids.get(str(row.floor_component),"INVALID")))
		bearing_witnesses += 1
	check(bearing_witnesses>=542,"All retained distributed slab bearings required")
	var parents: Dictionary = {}
	for edge in audit.full_chosen_contact_network:
		var name := str(edge.part)
		check(not parents.has(name),"Duplicate contact parent")
		check(float(edge.volume_overlap_m3)>0.00000001 or float(edge.contact_area_if_seam_m2)>0.00000001,"Point/line-only architectural join: "+name)
		check(float(edge.y_overlap[1])>=float(edge.y_overlap[0])-0.00000001,"Disconnected vertical contact: "+name)
		parents[name] = str(edge.support)
	check(audit.new_part_join_ledger.size()==598 and audit.all_new_to_old_contacts.size()==3856,"Complete new join/bearing census changed")
	var joined: Dictionary = {}
	for edge in audit.new_part_join_ledger:
		var name := str(edge.part)
		check(parts.has(name) and not joined.has(name) and parents.get(name,"")==str(edge.support),"Individual join ledger mismatch")
		joined[name] = true
	for name in parts:
		var current: String = name
		var visited: Dictionary = {}
		while not roots.has(current) and parents.has(current) and not visited.has(current):
			visited[current] = true
			if not glass.has(name):
				check(not glass.has(current),"Opaque structure relies on protective glass: "+name)
			current = str(parents[current])
		check(roots.has(current),"Unrooted/cyclic actual-source join: "+name)
	for label in audit.protected_queries:
		var row: Dictionary = audit.protected_queries[label]
		check(row.hits.is_empty(),"Source protected volume obstructed: "+str(label))
		var b: Array = row.bounds
		var inset := 0.002
		assert_empty(AABB(Vector3(b[0]+inset,b[2]+inset,b[4]+inset),Vector3(b[1]-b[0]-2*inset,b[3]-b[2]-2*inset,b[5]-b[4]-2*inset)),enclosure_exclusions,"Actual new intrusion "+str(label))
	check(data.doors.is_empty() and data.light_markers.is_empty(),"No new controllers, doors or lights authorized")
	check(enclosure.find_children("*","Light3D",true,false).is_empty(),"Enclosure added unapproved runtime light")
	check(audit.all25fixture_near_exits.size()==25 and audit.onward_full_downward_optical_cone.raised_header_hits.is_empty() and float(audit.onward_full_downward_optical_cone.half_angle)==82.0,"Correct82-degree existing optical cone proof missing")
	for row in audit.all25fixture_near_exits:
		check(row.new_material_exit_hits.is_empty() and float(row.half_angle_degrees)==82.0,"Existing fixture exit newly blocked")
		var marker := shell.find_child(str(row.marker),true,false) as Node3D
		if not check(marker!=null,"Retained optical source absent"):
			continue
		for depth in [0.01,0.04,0.12]:
			for index in range(32):
				var angle := TAU*float(index)/32.0
				var radius := tan(deg_to_rad(82.0))*float(depth)
				var target := marker.global_position+Vector3(cos(angle)*radius,-float(depth),sin(angle)*radius)
				check(ray(marker.global_position,target,enclosure_exclusions).is_empty(),"Actual82-degree near-source cone blocked: "+str(row.marker))

func validate_windows(data: Dictionary) -> void:
	check(data.windows.size()==28,"All28 framed protective windows required")
	for window in data.windows:
		var a := Vector3.ZERO
		var b := Vector3.ZERO
		var heights: Array = window.get("glass_y",[])
		if window.has("glass_aabb"):
			var bounds: Array = window.glass_aabb
			a = Vector3(float(window.position[0]),0,float(bounds[4]))
			b = Vector3(float(window.position[0]),0,float(bounds[5]))
			heights = [bounds[2],bounds[3]]
		else:
			a = Vector3(window.a_xz[0],0,window.a_xz[1])
			b = Vector3(window.b_xz[0],0,window.b_xz[1])
		var tangent := (b-a).normalized()
		var normal := Vector3(tangent.z,0,-tangent.x)
		var steps := maxi(2,ceili(a.distance_to(b)/0.45))
		for index in range(1,steps):
			var p := a.lerp(b,float(index)/steps)
			for fraction in [0.05,0.25,0.5,0.75,0.95]:
				p.y = lerpf(float(heights[0]),float(heights[1]),fraction)
				for sign_side in [-1.0,1.0]:
					var hit := ray(p+normal*0.10*sign_side,p-normal*0.10*sign_side,enclosure_exclusions)
					check(not hit.is_empty() and absf(hit.position.distance_to(p)-0.03)<EPS,"Missing/thickened protective pane face: "+str(window.id)+" at"+str(p))
	# Full8m onward mouth remains open below unchanged fixture/header level.
	for x in [-3.99,-3.0,0.0,3.0,3.99]:
		for y in [106.6,107.4,108.2,109.4,110.39]:
			check(ray(Vector3(x,y,193.0),Vector3(x,y,202.0),enclosure_exclusions).is_empty(),"New enclosure blocks8m onward opening")

func run() -> void:
	for path in PINS:
		check(FileAccess.get_sha256("res://"+str(path))==str(PINS[path]),"Reviewed final/preserved identity changed: "+str(path))
	var preserved: Dictionary = JSON.parse_string(PRESERVED_HASHES_JSON)
	for path in preserved:
		check(FileAccess.get_sha256("res://"+str(path))==str(preserved[path]),"Protected core/programme identity changed: "+str(path))
	var data := read_json(CONTRACT)
	var proof := read_json(ROUNDTRIP)
	var audit := read_json(AUDIT)
	var geometry := read_json(PARTS)
	if data.is_empty() or proof.is_empty() or audit.is_empty() or geometry.is_empty():
		quit(1)
		return
	for id in ["AST-CMD-005","AST-CMD-006"]:
		check(bool(proof[id].get("pass",false)) and bool(proof[id].get("source_closed_outward",false)) and bool(proof[id].get("exact_float32_oriented_position_triangle_uv_material_equality",false)),"Exact closed source/export proof missing: "+id)
		check(str(proof[id].export_sha256)==str(PINS["assets/models/"+id+".glb"]),"Paired source/export identity mismatch")
	var main := (load("res://scenes/main.tscn") as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(30):
		await physics_frame
	ship = main.get_node("World360/Astraea") as Node3D
	platform = ship.get_node_or_null("ShipSpace/Districts/AftCrownPlatform_WIP") as Node3D
	var enclosure_root := ship.get_node_or_null("ShipSpace/Districts/UpperHorizonEnclosure_WIP") as Node3D
	floors = ship.find_child("CompiledStructuralFloors_NotFinishedRooms",true,false) as Node3D
	if not check(platform!=null and enclosure_root!=null and floors!=null,"Actual retained platform/floors or new enclosure root missing"):
		quit(1)
		return
	var platform_shell := platform.get_node_or_null("AftCrownPlatformArchitecture") as Node3D
	enclosure = enclosure_root.get_node_or_null("UpperHorizonEnclosureArchitecture") as Node3D
	if not check(platform_shell!=null and enclosure!=null,"Actual architecture missing"):
		quit(1)
		return
	check(enclosure.global_transform.is_equal_approx(Transform3D.IDENTITY) and platform_shell.global_transform.is_equal_approx(Transform3D.IDENTITY),"Reviewed paired source placement changed")
	space = ship.get_world_3d().direct_space_state
	for body in ship.find_children("*","CollisionObject3D",true,false):
		var dynamic: bool = not body is StaticBody3D or body is AnimatableBody3D
		if dynamic:
			dynamic_exclusions.append(body.get_rid())
		if not enclosure.is_ancestor_of(body):
			enclosure_exclusions.append(body.get_rid())
		if not platform_shell.is_ancestor_of(body):
			shell_exclusions.append(body.get_rid())
		if dynamic or platform_shell.is_ancestor_of(body):
			own_exclusions.append(body.get_rid())
		if not floors.is_ancestor_of(body):
			slab_exclusions.append(body.get_rid())
	shell = enclosure
	validate_meshes(proof["AST-CMD-006"])
	enclosure_triangles = matched_triangles
	matched_triangles = 0
	shell = platform_shell
	asset_path = "res://assets/models/AST-CMD-005.glb"
	expected_batches = 964
	validate_meshes(proof["AST-CMD-005"])
	validate_floors()
	validate_core()
	var platform_data := read_json("res://data/architecture/AFT_CROWN_PLATFORM_RUNTIME.json")
	validate_piers(platform_data)
	validate_fixtures(platform_data)
	validate_contacts(data,audit,geometry)
	validate_windows(data)
	print(("UPPER HORIZON ENCLOSURE STRUCTURE PASS: " if failures.is_empty() else "UPPER HORIZON ENCLOSURE STRUCTURE FAILED: ")+"%d new/%d paired oriented triangles, max error %.9fm; %d solid faces, %d actual slab bearings, %d fixed floor owners/%d floor triangles, %d pier slices/%d keel rays; %d failures. Architectural geometry only." % [enclosure_triangles,matched_triangles,maximum_corner_error,solid_witnesses,bearing_witnesses,floor_owners,matched_floor_triangles,pier_slices,keel_rays,failures.size()])
	main.queue_free()
	await process_frame
	quit(0 if failures.is_empty() else 1)
