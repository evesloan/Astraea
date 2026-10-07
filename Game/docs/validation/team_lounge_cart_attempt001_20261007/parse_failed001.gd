extends "res://tests/medical_test_scene.gd"
# Scratch-staged, UNRUN. One explicit fixture, then ordinary input events only.
const PINS: Dictionary = {"res://project.godot":"42dfd175fd8135e51094d66347802a51f6622475a06b4b2c11227af29884bdc0","res://scenes/main.tscn":"d8cb8e406affb855439d3e66fc6ebe49e1220ce4751487197b88a25e41ca849d","res://scripts/player.gd":"990e825c7cd08d2b26760be7436c342188a85fbe1cc60f704fd009ac1d71aaa3","res://scripts/cleaning_cart.gd":"f0d8e2aef841737eb80cd1f9cee1104fa91491a57ae881fa8bf7fbbee1e593b0","res://scripts/cleaning_bottle.gd":"30d0daaf512ee9b0a0979b2d9dc77b657378c88997aeaced4eeb1d906b62341f","res://scripts/physics_tether.gd":"8a721666a96b496e989687b8c98c6467db4bd74e2b25ecb06bb316f8d46aa2cb","res://scripts/cart_handle.gd":"89a3ed537f9761f58b1840425143361dfe166f20b06af95a74edebe1e1aca488","res://scripts/team_lounge_receiving.gd":"a4111d6afb4581135fb2d85aaa6f6cd80953a1e6f4c5a3bae03f26116f1b0642","res://tests/medical_test_scene.gd":"ceeb6f7217927d706673b262a8b1d77693246aec57435dded147237499dd0ff8","res://tests/grand_pool_cart_probe.gd":"ea995180233238cb437862350c59cad34f3ec7176275f989d8ccfd7588c4f9b3","res://tests/medical_triage_successor_guard.gd":"7e166dd2475e78a3ecd2b244d5002be76a6d0264be0ffaa355f13ae6432e32e9","res://tests/fixtures/team_lounge_access001.json":"e05fc4b7181ed1645acaec9025f3cce7e6cfc7dc353a5e707ff38b1e63c54e01","res://data/architecture/cleaning_cart_contacts.json":"30a5de9043d6cbfdef2c75e471ec1ffa73c64500065e4af6093c0120aa04ad37","res://data/architecture/team_lounge/runtime_manifest.json":"acef0ad879687c15c87a2092907b25f9fac80c522179da6e0c020f0c4be6e987","res://data/architecture/team_lounge/source/WP15_team_lounge_source.glb.archive":"b2afb9a77e892c813123924f9e3b62ebcef230896e95846b6c29cd488a917ae0","res://assets/models/WP15_team_lounge_runtime_compartment_material_v1.glb":"292eeb623ca272882ea051aa37abecd5cdce80802c272234edcdf331ee1e3e6e","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_fore_team_room_static.faces":"1c81f51c361f2e65a2aa98ba41c5e571ca53a58b5f356b82f122f26beebea764","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_fore_team_room_N0527.faces":"8381628d8deec22169c3ec3a9b741e3e18da99d31eb6ac1178c6bd54db602cf8","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_fore_team_room_N0536.faces":"8381628d8deec22169c3ec3a9b741e3e18da99d31eb6ac1178c6bd54db602cf8","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_fore_team_room_N0545.faces":"8381628d8deec22169c3ec3a9b741e3e18da99d31eb6ac1178c6bd54db602cf8","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_fore_team_room_N0554.faces":"8381628d8deec22169c3ec3a9b741e3e18da99d31eb6ac1178c6bd54db602cf8","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_fore_team_room_N0563.faces":"8381628d8deec22169c3ec3a9b741e3e18da99d31eb6ac1178c6bd54db602cf8","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_fore_team_room_N0572.faces":"8381628d8deec22169c3ec3a9b741e3e18da99d31eb6ac1178c6bd54db602cf8","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_fore_team_room_N0581.faces":"8381628d8deec22169c3ec3a9b741e3e18da99d31eb6ac1178c6bd54db602cf8","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_fore_team_room_N0590.faces":"8381628d8deec22169c3ec3a9b741e3e18da99d31eb6ac1178c6bd54db602cf8","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_aft_quiet_room_static.faces":"72532267075b68a1a11e14c4dabd3be14ac2b2fdd8d983fd73de93b3a705cee4","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_aft_quiet_room_N1120.faces":"8381628d8deec22169c3ec3a9b741e3e18da99d31eb6ac1178c6bd54db602cf8","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_aft_quiet_room_N1129.faces":"8381628d8deec22169c3ec3a9b741e3e18da99d31eb6ac1178c6bd54db602cf8","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_aft_quiet_room_N1138.faces":"8381628d8deec22169c3ec3a9b741e3e18da99d31eb6ac1178c6bd54db602cf8","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_aft_quiet_room_N1147.faces":"8381628d8deec22169c3ec3a9b741e3e18da99d31eb6ac1178c6bd54db602cf8","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_aft_quiet_room_N1156.faces":"8381628d8deec22169c3ec3a9b741e3e18da99d31eb6ac1178c6bd54db602cf8","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_aft_quiet_room_N1165.faces":"8381628d8deec22169c3ec3a9b741e3e18da99d31eb6ac1178c6bd54db602cf8","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_aft_quiet_room_N1174.faces":"8381628d8deec22169c3ec3a9b741e3e18da99d31eb6ac1178c6bd54db602cf8","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_aft_quiet_room_N1183.faces":"8381628d8deec22169c3ec3a9b741e3e18da99d31eb6ac1178c6bd54db602cf8","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_arrival_neck_static.faces":"2940bfdac99c691d963916099f111bbf688d542f858e05bca1751e7faa26f0a1","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_arrival_neck_N1228.faces":"cc6b356675731fcde9dd92d49d67738dbc58d25f6d284bfc7983c525e51ceeda","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_arrival_neck_N1230.faces":"30d2990b1f14c9e96792768b2415b5c808b2b592e3898bb130ea32cd29e5ae25","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_arrival_neck_N1248.faces":"8381628d8deec22169c3ec3a9b741e3e18da99d31eb6ac1178c6bd54db602cf8","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_arrival_neck_N1257.faces":"8381628d8deec22169c3ec3a9b741e3e18da99d31eb6ac1178c6bd54db602cf8","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_arrival_neck_N1266.faces":"8381628d8deec22169c3ec3a9b741e3e18da99d31eb6ac1178c6bd54db602cf8","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_arrival_neck_N1275.faces":"8381628d8deec22169c3ec3a9b741e3e18da99d31eb6ac1178c6bd54db602cf8","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_support_annex_static.faces":"6fefa7bd929e44f3c92b789ae2d24ab2c4ad8406f365f778baa1421bd3614f7d","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_support_annex_N1287.faces":"fe84422492894418d801eb030ee42545a236cf1ef02fe6645c1d6b9d4381a9f2","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_support_annex_N1289.faces":"998cee5c2f61e6bf644e76bc5672574db778213fe19c36b2c3b0dc5339130e3b","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_support_annex_N1290.faces":"54a9af7a041aabaebd5d2b6a6f95662ba5a191bec3dd43043e09e3bc181e2649","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_support_annex_N1291.faces":"b26d6ae31b429fa8612b208fa16c2205cd98f3851a8dab44b6ec85b22ec40809","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_support_annex_N1292.faces":"ba1d1d1f0225efc85313bfaf416c9b51a5c91f9802e0dc91e8bc7fe6e2a25d30","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_support_annex_N1293.faces":"e66d591e16ef53e2a6726518727cf8a1ad3b35e72d1171eb328ad3e31ca7507c","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_support_annex_N1294.faces":"ed52191979cdd3965b4c09ee59b25e3a100a58f1bb11c5417ce7aad6e8682f5d","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_support_annex_N1295.faces":"5a763910c0f10f32465e6367e63ada67f94f92fe98ce5126a97278eafd76cbe3","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_support_annex_N1296.faces":"cd08b18fab94ab18ffd159189deed916cf2e543f447ffbf49db4f685e49bb3e7","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_support_annex_N1301.faces":"852f089bb676f23622afd8ca56104fab03bd41d952fedfec903347c9122129d7","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_support_annex_N1302.faces":"3dfa8c864db710b8908967413bec8449667ce10a02e8ef399bdbcc68139e7225","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_support_annex_N1303.faces":"fd2de6021b67a4e4a25d5a6ff45fc51ea54e11c19d7e4d96922102ea712e7b4b","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_support_annex_N1311.faces":"a1a4896f62fa1aa48aaf298a1aebc9338ef9b886734b0be00961ef1f95fdee87","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_support_annex_N1312.faces":"c5adeec2bc5b0364125b033595c0b8e792e977ce86ed7bad09c5bd837cf28443","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_support_annex_N1313.faces":"48812b2895badcf24ae0cea2552712b6761300dcadc6f003d49bf22a2dd7d1c1","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_support_annex_N1384.faces":"3244ada62545707ae1902315f1613b3eddf009a0208056b215f0623456caa1da","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_support_annex_N1385.faces":"22780b0bca5fbbd7fa0f75249b0befd9835c282319096900661d6ef77dd41ba2","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_support_annex_N1386.faces":"f5568583a168626ed8a1850267da67fdab33e509883a41e178e1c9e72b714670","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_support_annex_N1387.faces":"dc27ea6646da256ac24ffc43fb9fed8625142d11523b7ec62a992a8a933fe4a6","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_support_annex_N1388.faces":"02874894a531b1466406930cd9db77fc3650d5829c637749560a0c5b11dff5f5","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_support_annex_N1389.faces":"f2abf9e06569f38c9fd08b616ce5f432429ed325061197a308172d4a57f4dd33","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_support_annex_N1391.faces":"f9a6bcf7d8a2c3295580c8c2350bfbbad02bd7354cc3ca501654ddf666bfdbdb","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_support_annex_N1393.faces":"0b03b8e741b868374d390164f048eca4e6d4c9e924c2b14a7a16da1a835dacbd","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_support_annex_N1394.faces":"38306a67f4b620dd4662fd7b20a69cbb0a82e7eb00a7effd6ee509461abf43c5","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_support_annex_N1395.faces":"340b18d07cc18974323068f9be36977ef79b238eb982f7eb65f189db9c81bc54","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_support_annex_N1423.faces":"2057985c24e4683ef69d2bdac748043fb6c2ee440245010d08ba6e3f0c2bb6aa","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_support_annex_N1424.faces":"298ff10b8afa317a9b6bb18b300236d4b35d254d46860fab3443e43157f97aed","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_support_annex_N1435.faces":"0482ebf2e6f422a6068cd2ad65f314080baa144b430ce5721179f3f2b157135a","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_support_annex_N1436.faces":"b4d958c6eb2952d2e893524a468ba50e55dca54795a5772c4d318adaf16594ce","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_support_annex_N1437.faces":"0f163349951967a0007efd52267cbc47b745377b115b4be0e59eeedbcd83bc8d","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_support_annex_N1438.faces":"a39858f3e0b6b8fbc502e27e777c9aa531b221de57ef6707408d82eadfd09566","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_support_annex_N1439.faces":"4b5c03d93cdb1258befb7050339fc9be203cb4c97e9a1b824740648cccace67e","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_support_annex_N1440.faces":"36f1df98bb31f24d9128affad01184efc1a56210521d64fe565af0b5f17d51f0","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_support_annex_N1441.faces":"bcb15459d72949e456f2a58823c02a6829d9f3ef901ae406f8821fee5fc16b90","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_support_annex_N1442.faces":"cd7484fb28a1185cf918bcf78c39ac455761cca6ccb676278436d7cedf640abf","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_support_annex_N1443.faces":"24d85e978b2d20c8cd5be948960d3946335fbbeb5abaa10d30bc5276a3b645c0","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_support_annex_N1444.faces":"f5927dd82e22be3ce8127968e398b6ad471972b42d8797b7b2c77a11c4711f73","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_support_annex_N1445.faces":"9b00c6d468c421dc89548188a7c8b2d9dc5a52f66a75ccc1b56d0ec42f0a3672","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_support_annex_N1446.faces":"63da7d434fbac8fe39c40ef17164eebecf0740cb43b84b39a08f8b93de1a2c7d","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_support_annex_N1447.faces":"3357506d9c472bf148783e5cda417de5b5aa18cfeb27490a2f53d8ad5dec0cee","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_support_annex_N1448.faces":"1e778f53358421e719336f026df9acb2d0114e40b6ed83f1a6f96efc7a7522ab","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_support_annex_N1449.faces":"9e9c6746590cdd8d279a34ce839f47cdea5aacfd0bd2ba6a41e4369db24d0577","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_support_annex_N1450.faces":"4cc62714bedfbe404d60db8a0719fbd8cd70544d3972fad58d1ad603abd2ff4a","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_support_annex_N1451.faces":"c70455bfb548cc8b41bb09a47c443fd89f42c249082ff23fffb7ceba07916e4f","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_support_annex_N1452.faces":"f88cb5500b74acc927753110d79d80d1d48bafd5504d3d3e93aa792ee1242d20","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_support_annex_N1453.faces":"e4f51ee8e34c5a37858335ec68e69ea0d7e044f77c97c35842c8198ca754cc73","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_support_annex_N1463.faces":"e0d048749531703c27431c61d6f037014a6c8b69625385ac9f64b128249d20bc","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_support_annex_N1476.faces":"6d09289533f4c4ca6131a983fe0a1a5abaa6a1d01324cfdd7f283d1e682c2771","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_support_annex_N1477.faces":"31e21fcbadee9365e0bc0c02fdcb167df831db6b8e529aaa477233396b3703d7","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_support_annex_N1478.faces":"f153ab266fd5b35182de22f5926618a2c7ae4adcb6a4290cfe1a8ba3563a7fc1","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_support_annex_N1479.faces":"bac8939b36b05fbecb5ac03e8b9c1e2ca0d6b8c49005f59c429ee5ba1dfe5fd3","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_support_annex_N1480.faces":"5f9649d937ba94e35521768fa3cda94ff3406af3fd27c3893b6908df9d2b18ae","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_support_annex_N1481.faces":"4576d13a0da4b0f016c5b979f3cc1a67efc0d9006f2122ae819bb3656e5b8155","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_support_annex_N1482.faces":"26f08947b4d4c3313f329fb868d3f1e1010d4301b28e608144a9f294221c8dc1","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_support_annex_N1483.faces":"176f5fc67515a0214271d40ea77ac054d3c7730c67cb72748bf35ad072d6476e","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_support_annex_N1484.faces":"04f5cd580d9f63c75a251c9aee04fb5264cf2512a921db6bf350edf2d7f27bf1","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_support_annex_N1485.faces":"bdf19370d5a6a5be614c8f5c806f5886ac0e22cbb8eabf49af7643940acd28f6","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_support_annex_N1486.faces":"72026d79398056e0b96510f3cefbec1da5fdff0cbc9fbd3e9aa4070ea95336fe","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_support_annex_N1487.faces":"87ee175ed61fdc3c5a19c93220bc8b59e87a62d0d1d95e754ceaeaefaac5ce7a","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_support_annex_N1488.faces":"861d786d0e349768e94b33bf27e9a6ab0b4a76a3f331394def42cb0e6f911e68","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_support_annex_N1489.faces":"7e5bb710cd6faa74daecdc5dad6a076de4b8fa63a7b6e8ad0ca956f980f42e1b","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_support_annex_N1490.faces":"97266507b7957a4cbd8867aa0958b9c598eff98a12eaa528f5469da59e772c80","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_support_annex_N1491.faces":"27991fb150f0dfc3fa73627f792b2bbe57bb1706898783162b14b42ecbfe332b","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_fore_team_room_N1670.faces":"8381628d8deec22169c3ec3a9b741e3e18da99d31eb6ac1178c6bd54db602cf8","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_fore_team_room_N1921.faces":"8381628d8deec22169c3ec3a9b741e3e18da99d31eb6ac1178c6bd54db602cf8","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_fore_team_room_N2172.faces":"8381628d8deec22169c3ec3a9b741e3e18da99d31eb6ac1178c6bd54db602cf8","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_fore_team_room_N2423.faces":"8381628d8deec22169c3ec3a9b741e3e18da99d31eb6ac1178c6bd54db602cf8","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_fore_team_room_N2674.faces":"8381628d8deec22169c3ec3a9b741e3e18da99d31eb6ac1178c6bd54db602cf8","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_fore_team_room_N2925.faces":"8381628d8deec22169c3ec3a9b741e3e18da99d31eb6ac1178c6bd54db602cf8","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_aft_quiet_room_N3176.faces":"8381628d8deec22169c3ec3a9b741e3e18da99d31eb6ac1178c6bd54db602cf8","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_aft_quiet_room_N3427.faces":"8381628d8deec22169c3ec3a9b741e3e18da99d31eb6ac1178c6bd54db602cf8","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_aft_quiet_room_N3678.faces":"8381628d8deec22169c3ec3a9b741e3e18da99d31eb6ac1178c6bd54db602cf8","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_aft_quiet_room_N3929.faces":"8381628d8deec22169c3ec3a9b741e3e18da99d31eb6ac1178c6bd54db602cf8","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_aft_quiet_room_N4180.faces":"8381628d8deec22169c3ec3a9b741e3e18da99d31eb6ac1178c6bd54db602cf8","res://data/architecture/team_lounge/contacts/WP15_CONTACT_FINAL_aft_quiet_room_N4431.faces":"8381628d8deec22169c3ec3a9b741e3e18da99d31eb6ac1178c6bd54db602cf8"}
const FLOOR := 35.5
var probe = preload("res://tests/grand_pool_cart_probe.gd").new()
var identities: Array = []
var trace: Array = []
var active_leg := "setup"
var input_frames := 0
var travelled := 0.0
var achieved: Array = []

func _initialize() -> void:
	test_name = "team_lounge_loaded_cart_raw_input001"
	call_deferred("run")

func write_receipt(status: String, detail: String = "") -> void:
	if receipt_path.is_empty(): return
	var out := {"status":status,"detail":detail,"test":test_name,"leg":active_leg,"frames":frames,"input_frames":input_frames,"operator_metres":travelled,"achieved":achieved,"trace":trace,"source_pins":PINS,"initial_fixture_placements":1,"later_transform_or_velocity_writes":0,"normal_player_physics_active":true,"controls":"RMB/E and W/A/S/D plus mouse-motion events","scope":"One original four-loose-product cart through D07 connector/deep threshold, fore-social cleaning turn, guest refreshment and used-return approach, physical reverse return and RMB/E release. No full cleaning circuits, staff workpoints, service gameplay, six-species fit, freehand comfort, or final art acceptance."}
	var f := FileAccess.open(receipt_path, FileAccess.WRITE)
	if f != null: f.store_string(JSON.stringify(out,"  ")+"\n")

func aim(yaw: float, pitch_value: float, bounded := true) -> void:
	var dy := wrapf(yaw-actor.rotation.y,-PI,PI)
	if bounded: dy = clampf(dy,-.5/60.0,.5/60.0)
	var event := InputEventMouseMotion.new()
	event.relative = Vector2(-dy/.002, -(pitch_value-float(actor.get("pitch")))/.002)
	Input.parse_input_event(event)
	Input.flush_buffered_events()

func loads_ok() -> bool:
	if not require(cart.products.size()==4,"Exactly four original products required"): return false
	for i in range(4):
		var p: RigidBody3D = cart.products[i]
		if not require(p.get_instance_id()==identities[i][0] and str(p.get("persistent_id"))==identities[i][1],"Product identity changed"): return false
		var q := cart.to_local(p.global_position)
		if not require(q.y>.78 and q.y<1.35 and absf(q.x)<.43 and absf(q.z)<.62,"Original loose product escaped tray"): return false
		if not require(not p.freeze and p.collision_layer!=0,"Product physics/collision disabled"): return false
	return true

func tick(held: bool) -> bool:
	var before := actor.global_position
	if not await advance(1,false): return false
	if not require(actor.is_physics_processing() and actor.gameplay_input_enabled,"Original player controls must stay active"): return false
	if not require(actor.global_position.distance_to(before)<.25,"Unexpected player displacement"): return false
	travelled += Vector2(actor.global_position.x-before.x,actor.global_position.z-before.z).length()
	if not require(absf(actor.global_position.y-FLOOR)<.08 and absf(cart.global_position.y-FLOOR)<.12 and cart.global_basis.y.dot(Vector3.UP)>.98,"Cart/player left supported D07 datum or cart tipped"): return false
	if not loads_ok(): return false
	if held and not require(cart.get("driver")==actor,"Original handle tether lost"): return false
	if frames%6==0:
		if not support_at(Vector3(actor.global_position.x,FLOOR,actor.global_position.z)): return false
		for wheel in probe.wheel_specs:
			var q: Array = wheel.center
			var foot := cart.global_transform*Vector3(q[0],0,q[2])
			if not support_at(Vector3(foot.x,FLOOR,foot.z)): return false
	if frames%15==0:
		probe.check_pose(ship,actor,cart,Vector3(cart.global_position.x,FLOOR+.03,cart.global_position.z),cart.global_rotation.y,FLOOR)
		if failed: return false
		trace.append({"frame":frames,"leg":active_leg,"cart":str(cart.global_position),"yaw":cart.global_rotation.y,"actor":str(actor.global_position),"speed":cart.linear_velocity.length()})
	return true

func grab(expected: bool) -> bool:
	release_inputs()
	var handle := cart.get_node("PhysicalCartHandle") as Node3D
	var delta := handle.global_position-actor.camera.global_position
	aim(atan2(-delta.x,-delta.z),atan2(delta.y,Vector2(delta.x,delta.z).length()),false)
	if expected and not require(actor.call("target_from_view")==handle,"RMB/E must target the actual handle"): return false
	focus(true)
	for i in range(2):
		if not await tick(not expected): return false
	key(KEY_E,true)
	for i in range(2):
		if not await tick(false): return false
	key(KEY_E,false);focus(false)
	if not require((cart.get("driver")==actor)==expected,"Normal RMB/E state mismatch"): return false
	return true

func axis_key(negative: Key, positive: Key, error: float, speed: float) -> void:
	# Brake through ordinary key release; no actor or rigid-body velocity writes.
	var brake := maxf(.035,absf(speed)*absf(speed)/32.0+.015)
	key(negative,error < -brake)
	key(positive,error > brake)

func drive(label: String, goal: Vector2, yaw: float) -> bool:
	active_leg=label
	var reference := Vector2(cart.global_position.x,cart.global_position.z)
	var reference_yaw := actor.rotation.y
	var max_frames := ceili(reference.distance_to(goal)/.65*60.0)+ceili(absf(wrapf(yaw-reference_yaw,-PI,PI))/.3*60.0)+900
	var quiet := 0
	for frame in range(max_frames):
		var actual := Vector2(cart.global_position.x,cart.global_position.z)
		reference=reference.move_toward(goal,.65/60.0)
		reference=actual+(reference-actual).limit_length(.20)
		reference_yaw += clampf(wrapf(yaw-reference_yaw,-PI,PI),-.3/60.0,.3/60.0)
		reference_yaw=cart.global_rotation.y+clampf(wrapf(reference_yaw-cart.global_rotation.y,-PI,PI),-.25,.25)
		aim(reference_yaw,0.0)
		var desired := Vector3(reference.x,FLOOR,reference.y)+Basis(Vector3.UP,actor.rotation.y)*Vector3(0,0,1.62)
		var error := actor.global_basis.inverse()*(desired-actor.global_position)
		var speed := actor.global_basis.inverse()*actor.velocity
		axis_key(KEY_A,KEY_D,error.x,speed.x)
		axis_key(KEY_W,KEY_S,error.z,speed.z)
		if not await tick(true): return false
		input_frames+=1
		var pose_ok := Vector2(cart.global_position.x,cart.global_position.z).distance_to(goal)<.45 and absf(wrapf(cart.global_rotation.y-yaw,-PI,PI))<.10
		var done := reference.distance_to(goal)<.001 and absf(wrapf(reference_yaw-yaw,-PI,PI))<.001 and error.length()<.07
		quiet = quiet+1 if pose_ok and done and cart.linear_velocity.length()<.08 and cart.angular_velocity.length()<.08 and actor.velocity.length()<.08 else 0
		if quiet>=60:
			release_inputs()
			achieved.append({"leg":label,"goal":str(goal),"actual":str(cart.global_position),"yaw":cart.global_rotation.y,"settled_frames":quiet})
			return true
	return require(false,"Bounded raw-input leg stalled: "+label+" toward "+str(goal))

func run() -> void:
	started=Time.get_ticks_msec()
	var args := OS.get_cmdline_user_args()
	receipt_path=args[0] if not args.is_empty() else "/tmp/team_lounge_loaded_cart_raw_input001.json"
	for path in PINS:
		if not require(FileAccess.get_sha256(path)==PINS[path],"Source pin changed: "+path): return
	main=(load("res://scenes/main.tscn") as PackedScene).instantiate();root.add_child(main)
	for frame in range(150): await physics_frame
	ship=main.get_node("World360/Astraea") as Node3D
	actor=ship.get_node("ShipSpace/PersistentActors/Player") as CharacterBody3D
	cart=ship.find_child("CustodialCart",true,false) as RigidBody3D
	floors=ship.find_child("CompiledStructuralFloors_NotFinishedRooms",true,false) as Node3D
	built=ship.get_node("ShipSpace/D07_TeamLounge_Receiving_WIP") as Node3D
	space=ship.get_world_3d().direct_space_state
	if not require(actor!=null and cart!=null and floors!=null and built!=null,"Actual installed main-scene actors required"): return
	var proof: Dictionary=load("res://tests/medical_triage_successor_guard.gd").validate_current(floors)
	if not require(bool(proof.get("validation_completed",false)),"Installed predecessor/Team Lounge world proof failed"): return
	if not require(actor.get_script().resource_path=="res://scripts/player.gd" and cart.get_script().resource_path=="res://scripts/cleaning_cart.gd","Original controllers required"): return
	probe.failed.connect(func(message: String) -> void: require(false,"Unchanged compound-cart clearance: "+message))
	var offsets: Array[Vector3]=[]
	for p in cart.products:
		offsets.append(cart.to_local(p.global_position));identities.append([p.get_instance_id(),str(p.get("persistent_id"))])
	# SOLE SETUP: original loaded cart on existing D07 spine, facing connector.
	cart.global_position=Vector3(0,FLOOR+.04,216);cart.rotation=Vector3(0,-PI/2,0)
	cart.linear_velocity=Vector3.ZERO;cart.angular_velocity=Vector3.ZERO;cart.sleeping=false
	for i in range(4):
		cart.products[i].global_position=cart.global_transform*offsets[i]
		cart.products[i].linear_velocity=Vector3.ZERO;cart.products[i].angular_velocity=Vector3.ZERO;cart.products[i].sleeping=false
	if not require(ship.arrive_at(Vector3(-1.62,FLOOR+.1,216),-PI/2),"Initial supported D07 fixture refused"): return
	if not await advance(60,false): return
	if not support_at(Vector3(0,FLOOR,216),"D07_aft_route"): return
	if not loads_ok() or not await grab(true): return
	var route: Array=[
		["connector",Vector2(6,216),-PI/2],
		["deep_threshold",Vector2(13,216),-PI/2],
		["room_choice",Vector2(31,216),-PI/2],
		["face_fore_room",Vector2(31,216),0.0],
		["fore_cleaning_approach",Vector2(31,210.7),0.0],
		["fore_social_ninety_degree_turn",Vector2(31,210.7),-PI/2],
		["fore_turn_back",Vector2(31,210.7),0.0],
		["reverse_to_axis",Vector2(31,216),0.0],
		["face_service",Vector2(31,216),-PI/2],
		["service_axis",Vector2(44,216),-PI/2],
		["face_refreshment",Vector2(44,216),0.0],
		["refreshment_lane",Vector2(44,212.6),0.0],
		["refreshment_turn",Vector2(44,212.6),-PI/2],
		["refreshment_guest_approach",Vector2(47.1,212.6),-PI/2],
		["refreshment_reverse",Vector2(44,212.6),-PI/2],
		["face_return_lane",Vector2(44,212.6),0.0],
		["reverse_to_return_lane",Vector2(44,218),0.0],
		["return_edge_turn",Vector2(44,218),-PI/2],
		["used_return_guest_approach",Vector2(47.1,218),-PI/2],
		["used_return_reverse",Vector2(44,218),-PI/2],
		["face_axis_return",Vector2(44,218),0.0],
		["axis_return",Vector2(44,216),0.0],
		["face_reverse_exit",Vector2(44,216),-PI/2],
		["reverse_deep_threshold",Vector2(13,216),-PI/2],
		["reverse_connector",Vector2(6,216),-PI/2],
		["original_spine_return",Vector2(0,216),-PI/2]]
	for step in route:
		var before_yaw := cart.global_rotation.y
		if not await drive(step[0],step[1],step[2]): return
		if step[0]=="fore_social_ninety_degree_turn":
			if not require(absf(wrapf(cart.global_rotation.y-before_yaw,-PI,PI))>deg_to_rad(80.0),"Actual social-room cleaning turn must exceed eighty degrees"): return
	active_leg="release_on_original_spine"
	if not await grab(false): return
	for frame in range(90):
		if not await tick(false): return
	if not require(cart.get("driver")==null and actor.get("held_interaction")==null,"Normal release must clear both owners"): return
	write_receipt("PASS")
	print("TEAM_LOUNGE_LOADED_CART_RAW_INPUT PASS ",travelled," operator metres")
	main.queue_free();await process_frame;quit(0)
