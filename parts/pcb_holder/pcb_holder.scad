hole_distance = 100.0-2*6.0;
material = 3.0;
hole_radius = 2.1;
eps = 0.1;
$fn=100;

difference()
{
    union()
    {
        translate([0, 0, -material/2])
            cube([hole_distance+2*(material+hole_radius), 2*(material+hole_radius), material], center=true); 
        translate([0, hole_radius+material/2+material, material+hole_radius])
            cube([hole_distance+2*(material+hole_radius), material, 2*(material+hole_radius)], center=true);
        translate([0, +hole_radius+material+material/2, -material/2])
            cube([hole_distance+2*(material+hole_radius), material, material], center=true);
    }
    translate([-hole_distance/2, 0, -(material+eps)])
        cylinder(r=hole_radius, h=material+2*eps);
    translate([+hole_distance/2, 0,  -(material+eps)])
        cylinder(r=hole_radius, h=material+2*eps);
    
    for(i=[-40:10:40])
        translate([i, hole_radius+material-eps, material+hole_radius])
            rotate([-90, 0, 0])
                cylinder(r=hole_radius, h=material+2*eps);
}
